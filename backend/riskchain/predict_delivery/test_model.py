from predict_delivery.model_rnn import RNNModel, create_dataloaders, load_npz
import torch
import numpy as np
import joblib
from supplychains.models import SupplyChain

from predict_delivery.encoders import (
    build_node_encoder,
    build_edge_encoder,
    encode_supplychain_chain,
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def predict_supplychain_delay(supply_chain,model,node_enc,edge_enc,scaler_y, maxlen=10):

    seq = encode_supplychain_chain(supply_chain, node_enc, edge_enc)

    arr = np.asarray(seq, dtype=np.float32)
    L = arr.shape[0]
    feat_dim = arr.shape[1]

    eff_L = min(L, maxlen)
    X_pad = np.zeros((1, maxlen, feat_dim), dtype=np.float32)  # Batch=1
    X_pad[0, :eff_L, :] = arr[:eff_L]
    lengths = np.array([eff_L], dtype=np.int64)

    X_t = torch.tensor(X_pad, dtype=torch.float32, device=device)
    len_t = torch.tensor(lengths, dtype=torch.int64, device=device)

    y_pred_scaled = model(X_t, len_t).detach().cpu().numpy().astype(np.float32).reshape(-1)[0]

    y_pred_real = scaler_y.inverse_transform([[y_pred_scaled]]).reshape(-1)[0]

    return y_pred_real, y_pred_scaled

def predict_supplychains_delay():
    input_size=50
    hidden_size=64
    num_layers=2
    output_size=1

    model = RNNModel(input_size, hidden_size, num_layers, output_size)
    model.load_state_dict(torch.load("predict_delivery/models/rnn_model_2.pt", map_location=device))
    model.eval()

    scaler_y = joblib.load("predict_delivery/models/scaler_y.pkl")

    node_enc = build_node_encoder()
    edge_enc = build_edge_encoder()

    for supply_chain in SupplyChain.objects.all():
        y_pred_real, y_pred_scaled = predict_supplychain_delay(supply_chain,model,node_enc,edge_enc, scaler_y)
        supply_chain.predicted_delay = y_pred_real
        supply_chain.save()