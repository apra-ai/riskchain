# predict_delivery/model_rnn.py

import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from torch.amp import autocast, GradScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# -----------------------------
# Data loading
# -----------------------------
def load_npz(filename: str = "supplychains_sequences.npz", maxlen: int = 10):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"NPZ nicht gefunden: {path}")

    data = np.load(path, allow_pickle=True)
    files = set(data.files)

    X_var = data["X"]
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
        arr = np.asarray(seq, dtype=np.float32)
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
# Dataloaders (ohne y-Skalierung)
# -----------------------------
def create_dataloaders(
    X,
    y,
    eff_len,
    batch_size: int = 64,
    test_size: float = 0.2,
    random_state: int = 42,
    use_cuda: bool = False,
):
    idx = np.arange(len(X))
    train_idx, test_idx = train_test_split(
        idx, test_size=test_size, random_state=random_state, shuffle=True
    )

    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    len_train, len_test = eff_len[train_idx], eff_len[test_idx]

    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32)
    len_train_t = torch.tensor(len_train, dtype=torch.int64)

    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.float32)
    len_test_t = torch.tensor(len_test, dtype=torch.int64)

    pin = bool(use_cuda)
    train_ds = TensorDataset(X_train_t, len_train_t, y_train_t)
    test_ds = TensorDataset(X_test_t, len_test_t, y_test_t)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=False, pin_memory=pin)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, pin_memory=pin)

    print(f"Train Batches: {len(train_loader)} | Test Batches: {len(test_loader)}")
    print(f"Batch Size: {batch_size} | Features: {X.shape[-1]} | Maxlen: {X.shape[1]}")

    return train_loader, test_loader, (train_idx, test_idx)


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

        idx = (lengths - 1).view(-1, 1).expand(len(lengths), output.size(2)).unsqueeze(1)
        last_outputs = output.gather(1, idx).squeeze(1)
        return self.fc(last_outputs).squeeze()


# -----------------------------
# Train / Eval (ohne Scaler)
# -----------------------------
def main():
    learning_rate = 0.0001
    num_epochs = 1000
    batch_size = 64
    maxlen = 10

    X, lengths, eff_len, y, feat_dim, maxlen = load_npz(maxlen=maxlen)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device_type = "cuda" if device.type == "cuda" else "cpu"
    use_cuda = (device.type == "cuda")
    print("Training on:", device)

    train_loader, test_loader, _ = create_dataloaders(
        X, y, eff_len,
        batch_size=batch_size,
        test_size=0.2,
        random_state=42,
        use_cuda=use_cuda,
    )

    model = RNNModel(
        input_size=feat_dim,
        hidden_size=128,
        num_layers=3,
        output_size=1,
        dropout=0.2
    ).to(device)

    criterion = nn.SmoothL1Loss(beta=1.0)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scaler = GradScaler(enabled=use_cuda)

    for epoch in range(1, num_epochs + 1):
        model.train()
        train_loss_sum = 0.0

        for X_batch, len_batch, y_batch in train_loader:
            X_batch = X_batch.to(device, non_blocking=use_cuda)
            y_batch = y_batch.to(device, non_blocking=use_cuda)
            len_cpu = len_batch.cpu()

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

        # Evaluation (direkt auf realen Werten)
        model.eval()
        y_true, y_pred = [], []
        with torch.no_grad():
            for X_batch, len_batch, y_batch in test_loader:
                X_batch = X_batch.to(device, non_blocking=use_cuda)
                y_batch = y_batch.to(device, non_blocking=use_cuda)
                len_cpu = len_batch.cpu()
                preds = model(X_batch, len_cpu)

                y_true.extend(y_batch.cpu().numpy())
                y_pred.extend(preds.cpu().numpy())

        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        val_mae = np.mean(np.abs(y_true - y_pred))
        r2 = r2_score(y_true, y_pred)

        print(
            f"Epoch [{epoch}/{num_epochs}] "
            f"Train Loss: {train_loss:.4f} | "
            f"Val MAE: {val_mae:.4f} | R²: {r2:.3f}"
        )

        torch.save(model.state_dict(), f"models/rnn_model_{epoch}.pt")


if __name__ == "__main__":
    main()
