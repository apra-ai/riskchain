# manage.py shell -c "exec(open('export_npz.py','r',encoding='utf-8').read())"
# export_npz.py
import numpy as np
from supplychains.models import SupplyChain
from predict_delivery.encoders import build_node_encoder, build_edge_encoder
from predict_delivery.encoders import encode_supplychain_chain  # deine Funktion

MAXLEN = 10  # oder dynamisch: max(len(seq)) über alle Chains
node_enc = build_node_encoder()
edge_enc = build_edge_encoder()

X_list, lengths, y_list = [], [], []

qs = SupplyChain.objects.all()
for sc in qs.iterator():
    seq = encode_supplychain_chain(sc, node_enc, edge_enc)  # List[List[int]]
    L = len(seq)
    lengths.append(L)
    feat_dim = len(seq[0]) if L else node_enc.dim + edge_enc.dim + node_enc.dim
    # Pad/Truncate
    arr = np.zeros((MAXLEN, feat_dim), dtype=np.float32)
    if L:
        arr[:min(L, MAXLEN), :feat_dim] = np.array(seq[:MAXLEN], dtype=np.float32)
    X_list.append(arr)
    # Ziel, Beispiel: Gesamt-Delay
    y_list.append(float(sc.get_delay_score()))

X_padded = np.stack(X_list)            # [N, MAXLEN, F]
lengths = np.array(lengths, dtype=np.int32)
y = np.array(y_list, dtype=np.float32)

np.savez_compressed(
    "supplychains_sequences.npz",
    X=X_padded, lengths=lengths, y=y,
    maxlen=MAXLEN, feat_dim=X_padded.shape[-1]
)
print("Gespeichert: supplychains_sequences.npz",
      X_padded.shape, lengths.shape, y.shape)

# load
# import numpy as np
# data = np.load("supplychains_sequences.npz")
# X = data["X"]          # [N, MAXLEN, F]
# lengths = data["lengths"]
# y = data["y"]