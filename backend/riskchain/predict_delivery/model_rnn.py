# predict_delivery/model_rnn.py

import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from torch.amp import autocast, GradScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import joblib

# -----------------------------
# Data loading (variable length -> padded to maxlen)
# -----------------------------
def load_npz(filename: str = "supplychains_sequences.npz", maxlen: int = 10):
    """
    Lädt variable Sequenzen (X als object-Array) und pad/truncate't zur Laufzeit auf `maxlen`.
    Rückgabe:
      X_padded: [N, maxlen, feat_dim] (float32)
      lengths : [N]  (Original-Längen)
      eff_len : [N]  (min(length, maxlen))
      y       : [N]  (float32)
      feat_dim: int
      maxlen  : int
    """
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"NPZ nicht gefunden: {path}")

    data = np.load(path, allow_pickle=True)
    files = set(data.files)

    X_var = data["X"]                      # array(dtype=object), jedes Element: (L_i, F)
    y = data["y"].astype(np.float32)
    lengths = data["lengths"].astype(np.int32) if "lengths" in files else np.array(
        [len(seq) for seq in X_var], dtype=np.int32
    )

    feat_dim = None
    if "feat_dim" in files:
        try:
            feat_dim = int(np.array(data["feat_dim"]).reshape(()).item())
        except Exception:
            feat_dim = None
    if feat_dim is None:
        for seq in X_var:
            if len(seq) > 0:
                feat_dim = int(np.asarray(seq).shape[-1])
                break
        if feat_dim is None:
            raise ValueError("feat_dim konnte nicht bestimmt werden (alle Sequenzen leer?).")

    N = len(X_var)
    X_padded = np.zeros((N, maxlen, feat_dim), dtype=np.float32)
    eff_len = np.zeros(N, dtype=np.int32)

    for i, seq in enumerate(X_var):
        arr = np.asarray(seq, dtype=np.float32)  # (L_i, F) oder (0,)
        L = arr.shape[0] if arr.ndim == 2 else 0
        L_eff = min(L, maxlen)
        eff_len[i] = L_eff
        if L_eff > 0:
            X_padded[i, :L_eff, :] = arr[:L_eff]

    print(f"✅ Daten geladen: {path}")
    print(f"Chains: {N} | Features: {feat_dim} | maxlen: {maxlen}")
    print(f"Ø Länge(orig): {np.mean(lengths):.2f} | Max(orig): {np.max(lengths)}")

    return X_padded, lengths, eff_len, y, feat_dim, maxlen


# -----------------------------
# Dataloaders (mit y-Skalierung nur auf Train)
# -----------------------------
def create_dataloaders(
    X,
    y,
    eff_len,
    batch_size: int = 64,
    test_size: float = 0.2,
    random_state: int = 42,
    scale_y: bool = True,
    existing_scaler: StandardScaler | None = None,
    use_cuda: bool = False,
):
    """
    Split in Train/Test, skaliert y NUR auf Basis der Trainingsdaten (falls scale_y=True),
    baut PyTorch DataLoader und liefert zusätzlich den verwendeten StandardScaler zurück.
    Rückgabe:
      train_loader, test_loader, scaler_y, (train_idx, test_idx)
    """
    idx = np.arange(len(X))
    train_idx, test_idx = train_test_split(
        idx, test_size=test_size, random_state=random_state, shuffle=True
    )

    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    len_train, len_test = eff_len[train_idx], eff_len[test_idx]

    scaler_y = existing_scaler
    if scale_y:
        if scaler_y is None:
            scaler_y = StandardScaler()
            y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).squeeze()
        else:
            y_train_scaled = scaler_y.transform(y_train.reshape(-1, 1)).squeeze()
        y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).squeeze()
    else:
        y_train_scaled = y_train
        y_test_scaled = y_test
        scaler_y = None

    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train_scaled, dtype=torch.float32)
    len_train_t = torch.tensor(len_train, dtype=torch.int64)

    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test_scaled, dtype=torch.float32)
    len_test_t = torch.tensor(len_test, dtype=torch.int64)

    pin = bool(use_cuda)
    train_ds = TensorDataset(X_train_t, len_train_t, y_train_t)
    test_ds = TensorDataset(X_test_t, len_test_t, y_test_t)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=False, pin_memory=pin)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, pin_memory=pin)

    print(f"Train Batches: {len(train_loader)} | Test Batches: {len(test_loader)}")
    print(f"Batch Size: {batch_size} | Features: {X.shape[-1]} | Maxlen: {X.shape[1]}")

    return train_loader, test_loader, scaler_y, (train_idx, test_idx)


# -----------------------------
# Model
# -----------------------------
class RNNModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
        super().__init__()
        self.rnn = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x, lengths):
        packed_input = nn.utils.rnn.pack_padded_sequence(
            x, lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        packed_output, _ = self.rnn(packed_input)
        output, _ = nn.utils.rnn.pad_packed_sequence(packed_output, batch_first=True)

        # letzter gültiger Zeitschritt je Sequenz
        idx = (lengths - 1).view(-1, 1).expand(len(lengths), output.size(2)).unsqueeze(1)
        last_outputs = output.gather(1, idx).squeeze(1)

        return self.fc(last_outputs).squeeze()


# -----------------------------
# Train / Eval
# -----------------------------
def main():
    # Hyperparameter
    learning_rate = 0.0001
    num_epochs = 1000
    batch_size = 64
    maxlen = 10

    # Daten
    X, lengths, eff_len, y, feat_dim, maxlen = load_npz(maxlen=maxlen)

    # Gerät
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device_type = "cuda" if device.type == "cuda" else "cpu"
    use_cuda = (device.type == "cuda")
    print("Training on:", device)

    # Dataloader
    train_loader, test_loader, scaler_y, _ = create_dataloaders(
        X, y, eff_len,
        batch_size=batch_size,
        test_size=0.2,
        random_state=42,
        scale_y=True,
        existing_scaler=None,
        use_cuda=use_cuda,
    )

    joblib.dump(scaler_y, "models/scaler_y.pkl")

    # Modell / Optimizer / Loss / AMP
    model = RNNModel(
        input_size=feat_dim,
        hidden_size=128,
        num_layers=3,
        output_size=1,
        dropout=0.2
    ).to(device)

    criterion = nn.SmoothL1Loss(beta=1.0)  # Huber
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scaler = GradScaler(enabled=use_cuda)

    # Training Loop
    for epoch in range(1, num_epochs + 1):
        model.train()
        train_loss_sum = 0.0

        for X_batch, len_batch, y_batch in train_loader:
            X_batch = X_batch.to(device, non_blocking=use_cuda)
            y_batch = y_batch.to(device, non_blocking=use_cuda)
            len_cpu = len_batch.cpu()  # pack_padded_sequence erwartet CPU

            optimizer.zero_grad(set_to_none=True)
            with autocast(device_type):
                preds = model(X_batch, len_cpu)
                loss = criterion(preds, y_batch)

            scaler.scale(loss).backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()

            train_loss_sum += loss.item() * X_batch.size(0)

        train_loss = train_loss_sum / len(train_loader.dataset)

        # Evaluation (auf skalierten Zielen)
        model.eval()
        y_true_scaled, y_pred_scaled = [], []
        with torch.no_grad():
            for X_batch, len_batch, y_batch in test_loader:
                X_batch = X_batch.to(device, non_blocking=use_cuda)
                y_batch = y_batch.to(device, non_blocking=use_cuda)
                len_cpu = len_batch.cpu()
                preds = model(X_batch, len_cpu)

                y_true_scaled.extend(y_batch.cpu().numpy())
                y_pred_scaled.extend(preds.cpu().numpy())

        y_true_scaled = np.array(y_true_scaled)
        y_pred_scaled = np.array(y_pred_scaled)

        # Metriken (skaliert)
        val_mae_scaled = np.mean(np.abs(y_true_scaled - y_pred_scaled))
        r2_scaled = r2_score(y_true_scaled, y_pred_scaled)

        # Optional: Metriken in Originaleinheiten (falls skaliert)
        if scaler_y is not None:
            y_true_real = scaler_y.inverse_transform(y_true_scaled.reshape(-1, 1)).squeeze()
            y_pred_real = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).squeeze()
            val_mae_real = np.mean(np.abs(y_true_real - y_pred_real))
            r2_real = r2_score(y_true_real, y_pred_real)
            print(
                f"Epoch [{epoch}/{num_epochs}] "
                f"Train Loss: {train_loss:.4f} | "
                f"Val MAE (scaled): {val_mae_scaled:.4f} | R² (scaled): {r2_scaled:.3f} | "
                f"Val MAE (real): {val_mae_real:.4f} | R² (real): {r2_real:.3f}"
            )
        else:
            print(
                f"Epoch [{epoch}/{num_epochs}] "
                f"Train Loss: {train_loss:.4f} | "
                f"Val MAE: {val_mae_scaled:.4f} | R²: {r2_scaled:.3f}"
            )
        torch.save(model.state_dict(), f"models/rnn_model_{epoch}.pt")


if __name__ == "__main__":
    main()
