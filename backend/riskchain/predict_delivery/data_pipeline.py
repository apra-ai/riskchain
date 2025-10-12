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

    X_list, lengths_list, eff_list, mask_list, y_list = [], [], [], [], []

    for sc in queryset.iterator():
        seq = encode_supplychain_chain(sc, node_enc, edge_enc)  # List[List[int]]
        if not seq:
            continue

        L = len(seq)
        eff_L = min(L, maxlen)

        arr = np.zeros((maxlen, feat_dim), dtype=np.float32)
        arr[:eff_L, :] = np.asarray(seq[:eff_L], dtype=np.float32)

        m = np.zeros((maxlen,), dtype=np.float32)
        m[:eff_L] = 1.0

        X_list.append(arr)
        lengths_list.append(L)        # Original
        eff_list.append(eff_L)        # effektiv genutzt
        mask_list.append(m)
        y_list.append(float(sc.get_delay_score()))

    if not X_list:
        raise ValueError("Keine nicht-leeren Sequenzen gefunden – nichts zu speichern.")

    X = np.stack(X_list, axis=0)                          # [N, maxlen, feat_dim]
    lengths = np.asarray(lengths_list, dtype=np.int32)    # [N]
    eff_len = np.asarray(eff_list, dtype=np.int32)        # [N]
    mask = np.stack(mask_list, axis=0)                    # [N, maxlen]
    y = np.asarray(y_list, dtype=np.float32)              # [N]

    np.savez_compressed(
        out_path,
        X=X,
        lengths=lengths,   # original
        eff_len=eff_len,   # min(original, maxlen)
        mask=mask,
        y=y,
        feat_dim=int(feat_dim),
        maxlen=int(maxlen),
    )

    print(f"✅ Gespeichert: {out_path}")
    print(f"Chains: {len(X)} | Feature-Dim: {feat_dim} | "
          f"ØLänge(orig): {np.mean(lengths):.2f} | Max(orig): {np.max(lengths)} | maxlen: {maxlen}")

    return out_path
