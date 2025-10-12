# export_npz_variable_length.py
import numpy as np
from supplychains.models import SupplyChain
from predict_delivery.encoders import build_node_encoder, build_edge_encoder
from predict_delivery.encoders import encode_supplychain_chain  # deine Funktion

node_enc = build_node_encoder()
edge_enc = build_edge_encoder()

X_list, lengths, y_list = [], [], []

qs = SupplyChain.objects.all()
for sc in qs.iterator():
    seq = encode_supplychain_chain(sc, node_enc, edge_enc)  # List[List[int]]
    if not seq:
        continue  # überspringe leere Chains
    L = len(seq)
    lengths.append(L)
    X_list.append(np.array(seq, dtype=np.float32))  # [L, F]
    y_list.append(float(sc.get_delay_score()))

# In ein NumPy-Objektarray umwandeln (variabel lange Sequenzen)
X = np.array(X_list, dtype=object)
lengths = np.array(lengths, dtype=np.int32)
y = np.array(y_list, dtype=np.float32)

np.savez_compressed(
    "supplychains_sequences.npz",
    X=X, lengths=lengths, y=y,
    feat_dim=X[0].shape[-1]
)

print("✅ Gespeichert: supplychains_sequences.npz")
print(f"Chains: {len(X)}, Feature-Dim: {X[0].shape[-1]}")
print(f"Durchschnittliche Länge: {np.mean(lengths):.2f}, Max: {np.max(lengths)}")


# load
import numpy as np

# data = np.load("supplychains_sequences.npz", allow_pickle=True)

# X = data["X"]           # dtype=object → jede Zelle ist ein np.ndarray mit Shape (Lᵢ, F)
# lengths = data["lengths"]
# y = data["y"]

# print(f"Anzahl Chains: {len(X)}")
# print(f"Beispiel: X[0].shape = {X[0].shape}, y[0] = {y[0]}")