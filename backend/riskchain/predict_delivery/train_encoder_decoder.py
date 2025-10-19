import os
import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from encoder_decoder_model import BiLSTMAttnEncoder, ARDecoder

# ================================
# CONFIG
# ================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Training on:", device)

# Hyperparameter
hid = 192
lr = 1e-4
teacher_forcing = 0.8
batch_size = 64
num_epochs = 100
test_split = 0.2
npz_path = "models/supplychains_sequences.npz"

# ================================
# 1️⃣ Dataset / Loader
# ================================
class Seq2SeqDataset(Dataset):
    def __init__(self, X, mask, Y, Y_mask):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.mask = torch.tensor(mask, dtype=torch.float32)
        self.Y = torch.tensor(Y, dtype=torch.float32)
        self.Y_mask = torch.tensor(Y_mask, dtype=torch.float32)
    def __len__(self):
        return self.X.shape[0]
    def __getitem__(self, idx):
        return self.X[idx], self.mask[idx], self.Y[idx], self.Y_mask[idx]


def load_npz_align(path: str):
    data = np.load(path, allow_pickle=True)

    X = data["X"].astype(np.float32)        # [N,T,F]
    mask = data["mask"].astype(np.float32)  # [N,T]
    y = data["y"].astype(np.float32)        # [N,Ty]
    y_mask = data["y_mask"].astype(np.float32)  # [N,Ty]

    N, T, F = X.shape
    Ty = y.shape[1]
    L = min(T, Ty)

    Y = np.zeros((N, T, 1), dtype=np.float32)
    Y_mask = np.zeros((N, T), dtype=np.float32)
    Y[:, :L, 0] = y[:, :L]
    Y_mask[:, :L] = y_mask[:, :L]
    Y_mask = Y_mask * mask  # Zielmasken <= Eingabemasken

    print(f"✅ Geladen: {path}")
    print(f"  X: {X.shape}, Y: {Y.shape}, feat_dim={F}, maxlen={T}")
    return X, mask, Y, Y_mask, F, T


# ================================
# 2️⃣ Train/Test Split + Dataloaders
# ================================
def make_dataloaders(X, mask, Y, Y_mask, batch_size=64, test_split=0.2, seed=42):
    N = X.shape[0]
    idx = np.arange(N)
    np.random.default_rng(seed).shuffle(idx)

    split = int(N * (1 - test_split))
    train_idx, test_idx = idx[:split], idx[split:]

    ds_train = Seq2SeqDataset(X[train_idx], mask[train_idx], Y[train_idx], Y_mask[train_idx])
    ds_test = Seq2SeqDataset(X[test_idx], mask[test_idx], Y[test_idx], Y_mask[test_idx])

    train_dl = DataLoader(ds_train, batch_size=batch_size, shuffle=True, drop_last=False)
    test_dl = DataLoader(ds_test, batch_size=batch_size, shuffle=False, drop_last=False)

    print(f"Train: {len(train_dl)} Batches | Test: {len(test_dl)} Batches")
    return train_dl, test_dl


# ================================
# 3️⃣ Load Data
# ================================
X, mask, Y, Y_mask, feat_dim, maxlen = load_npz_align(npz_path)
train_loader, test_loader = make_dataloaders(X, mask, Y, Y_mask, batch_size, test_split)

# ================================
# 4️⃣ Model + Optimizer + Loss
# ================================
encoder = BiLSTMAttnEncoder(x_dim=feat_dim, hid=hid).to(device)
decoder = ARDecoder(x_dim=feat_dim, y_dim=1, hid=hid, use_attention=True).to(device)
params = list(encoder.parameters()) + list(decoder.parameters())
optimizer = optim.Adam(params, lr=lr)
criterion = torch.nn.SmoothL1Loss(reduction="none")

# ================================
# 5️⃣ Training Loop
# ================================
for epoch in range(1, num_epochs + 1):
    encoder.train()
    decoder.train()
    train_loss_sum, n_train = 0.0, 0

    for Xb, Mb, Yb, YMb in train_loader:
        Xb, Mb, Yb, YMb = Xb.to(device), Mb.to(device), Yb.to(device), YMb.to(device)
        optimizer.zero_grad()

        H_enc = encoder(Xb, Mb)
        Y_pred = decoder(H_enc, Mb, Xb, Yb, teacher_forcing=teacher_forcing)

        # maskierter Loss
        loss_raw = criterion(Y_pred, Yb).squeeze(-1) * YMb
        loss = loss_raw.sum() / YMb.sum()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        optimizer.step()

        train_loss_sum += loss.item() * Xb.size(0)
        n_train += Xb.size(0)

    train_loss = train_loss_sum / max(1, n_train)

    # --- Evaluation (autoregressiv) ---
    encoder.eval()
    decoder.eval()
    val_loss_sum, val_mae_sum, n_val = 0.0, 0.0, 0
    with torch.no_grad():
        for Xb, Mb, Yb, YMb in test_loader:
            Xb, Mb, Yb, YMb = Xb.to(device), Mb.to(device), Yb.to(device), YMb.to(device)
            H_enc = encoder(Xb, Mb)
            Y_pred = decoder.infer(H_enc, Mb, Xb, Y_prefix=None, k=0)

            # maskierter Loss
            diff = (Y_pred - Yb).squeeze(-1)
            loss_raw = criterion(Y_pred, Yb).squeeze(-1) * YMb
            loss = loss_raw.sum() / YMb.sum()

            # maskierter MAE
            mae_raw = diff.abs() * YMb
            mae = mae_raw.sum() / YMb.sum()

            val_loss_sum += loss.item() * Xb.size(0)
            val_mae_sum += mae.item() * Xb.size(0)
            n_val += Xb.size(0)

    val_loss = val_loss_sum / max(1, n_val)
    val_mae = val_mae_sum / max(1, n_val)

    print(f"Epoch {epoch:03d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val MAE: {val_mae:.4f}")
    # am Ende deiner Trainingsschleife
    checkpoint = {
        "epoch": epoch,
        "encoder_state_dict": encoder.state_dict(),
        "decoder_state_dict": decoder.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "train_loss": train_loss,
        "val_loss": val_loss,
    }
    os.makedirs("models", exist_ok=True)
    torch.save(checkpoint, f"models/encoder_decoder_epoch_v2_{epoch:03d}.pt")

# ================================
# 6️⃣ Save Model
# ================================
os.makedirs("models", exist_ok=True)
torch.save(
    {"encoder": encoder.state_dict(), "decoder": decoder.state_dict()},
    "models/seq2seq_bilstm_attn.pt"
)
print("✅ Model saved to models/seq2seq_bilstm_attn.pt")
