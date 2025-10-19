# predict_delivery/data_pipeline.py

import os
import numpy as np
from django.conf import settings
from django.db.models import Prefetch
from supplychains.models import SupplyChain, ChainStep
from predict_delivery.encoders import (
    build_node_encoder,
    build_edge_encoder,
    encode_supplychain_chain,
)

def build_npz(
    output_filename: str = "supplychains_sequences.npz",
    queryset=None,
    maxlen: int = 10,  # << neue feste Sequenzlänge fürs Training
) -> str:
    """
    Exportiert SupplyChains als gepaddete/ggf. gekürzte Sequenzen.
    Speichert:
      - X:        [N, maxlen, feat_dim] (float32)
      - lengths:  [N]  (Original-Längen vor Kürzung/Padding)
      - eff_len:  [N]  (min(length, maxlen))
      - mask:     [N, maxlen]  (1=realer Schritt, 0=Padding)
      - y:        [N]
      - feat_dim, maxlen (Metadaten)
    """
    out_path = os.path.join(settings.BASE_DIR, output_filename)

    node_enc = build_node_encoder()
    edge_enc = build_edge_encoder()
    feat_dim = node_enc.dim + edge_enc.dim + node_enc.dim  # Schritt-Feature-Dim

    # performant laden: Steps + Edge + Nodes gleich mitziehen
    if queryset is None:
        queryset = SupplyChain.objects.prefetch_related(
            Prefetch(
                "steps",
                queryset=ChainStep.objects.select_related(
                    "edge", "edge__from_node", "edge__to_node"
                ).order_by("position"),
            )
        )

    X_list, lengths_list, eff_list, mask_list, y_raw_list = [], [], [], [], []

    for sc in queryset.iterator(chunk_size=1000):
        seq = encode_supplychain_chain(sc, node_enc, edge_enc)
        if not seq:
            continue

        L = len(seq)
        eff_L = min(L, maxlen)

        arr = np.zeros((maxlen, feat_dim), dtype=np.float32)
        arr[:eff_L, :] = np.asarray(seq[:eff_L], dtype=np.float32)

        m = np.zeros((maxlen,), dtype=np.float32)
        m[:eff_L] = 1.0

        X_list.append(arr)
        lengths_list.append(L)
        eff_list.append(eff_L)
        mask_list.append(m)

        # NEU: y als Liste sammeln (unterschiedliche Länge)
        y_vals = sc.get_seperated_delay_score()                 # <- jetzt Liste
        y_raw_list.append(np.asarray(y_vals, dtype=np.float32))

    if not X_list:
        raise ValueError("Keine nicht-leeren Sequenzen gefunden – nichts zu speichern.")

    # Stapeln von X/Masken wie gehabt
    X = np.stack(X_list, axis=0)                       # [N, maxlen, feat_dim]
    lengths = np.asarray(lengths_list, dtype=np.int32) # [N]
    eff_len = np.asarray(eff_list, dtype=np.int32)     # [N]
    mask = np.stack(mask_list, axis=0)                 # [N, maxlen]

    # --- NEU: y padden ---
    N = len(y_raw_list)
    y_len = np.asarray([len(v) for v in y_raw_list], dtype=np.int32)   # [N] Original-Längen
    y_maxlen = int(y_len.max())                                        # Padding-Länge = max beobachtet
    y = np.zeros((N, y_maxlen), dtype=np.float32)                      # [N, y_maxlen]
    y_mask = np.zeros((N, y_maxlen), dtype=np.float32)                 # [N, y_maxlen]

    for i, v in enumerate(y_raw_list):
        L = len(v)
        y[i, :L] = v
        y_mask[i, :L] = 1.0

    np.savez_compressed(
        out_path,
        X=X,
        lengths=lengths,    # Original-Länge der Schritte (X)
        eff_len=eff_len,    # min(original, maxlen) für X
        mask=mask,

        # Targets:
        y=y,                # gepaddet [N, y_maxlen]
        y_len=y_len,        # Original-Längen je Sample
        y_mask=y_mask,      # 1=realer Wert, 0=Padding
        y_maxlen=y_maxlen,  # Meta

        feat_dim=int(feat_dim),
        maxlen=int(maxlen),
    )

    print(f"✅ Gespeichert: {out_path}")
    print(
        f"Chains: {len(X)} | X-Feat-Dim: {feat_dim} | "
        f"ØLänge(X orig): {np.mean(lengths):.2f} | Max(X orig): {np.max(lengths)} | maxlen: {maxlen} | "
        f"y_maxlen: {y_maxlen} | ØLänge(y): {np.mean(y_len):.2f}"
    )

    return out_path
