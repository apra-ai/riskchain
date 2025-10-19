import torch
import torch.nn as nn

# ----- dein Encoder bleibt wie gepostet -----
# BiLSTMAttnEncoder(x_dim, hid=128, attn_heads=4, dropout=0.1)

def masked_mean(x, mask):
    # x:[B,T,H], mask:[B,T] (1 echt, 0 pad) -> [B,H]
    m = mask.unsqueeze(-1)                # [B,T,1]
    s = (x * m).sum(dim=1)                # [B,H]
    d = m.sum(dim=1).clamp_min(1e-6)      # [B,1]
    return s / d

class LuongAttention(nn.Module):
    """'general' Luong-Attention: score(h_t, H_enc) = h_t W H_enc^T"""
    def __init__(self, hid):
        super().__init__()
        self.W = nn.Linear(hid, hid, bias=False)

    def forward(self, h_t, H_enc, enc_mask):
        # h_t:[B,H], H_enc:[B,T,H], enc_mask:[B,T] (1 echt, 0 pad)
        Wh = self.W(h_t).unsqueeze(1)           # [B,1,H]
        scores = torch.bmm(Wh, H_enc.transpose(1,2)).squeeze(1)  # [B,T]
        scores = scores.masked_fill(enc_mask == 0, -1e9)
        attn = torch.softmax(scores, dim=-1)    # [B,T]
        ctx = torch.bmm(attn.unsqueeze(1), H_enc).squeeze(1)     # [B,H]
        return ctx, attn                         # Kontext + Gewichte (optional)

class ARDecoder(nn.Module):
    """
    Autoregressiver Decoder:
      Input pro Schritt: concat([y_prev, x_t, context_t])
      Core: LSTMCell
      Output: y_t
    """
    def __init__(self, x_dim, y_dim=1, hid=128, use_attention=True, dropout=0.1):
        super().__init__()
        self.use_attention = use_attention
        self.attn = LuongAttention(hid) if use_attention else None
        in_dim = y_dim + x_dim + (hid if use_attention else 0)

        self.cell = nn.LSTMCell(in_dim, hid)
        self.out = nn.Linear(hid, y_dim)
        self.drop = nn.Dropout(dropout)

        # Projektoren, um Decoder-Startzustand aus Encoder-Pooling zu initialisieren
        self.h0_proj = nn.Linear(hid, hid)
        self.c0_proj = nn.Linear(hid, hid)

    def init_state_from_encoder(self, H_enc, enc_mask):
        # masked mean pooling der Encoder-Ausgaben
        pooled = masked_mean(H_enc, enc_mask)      # [B,H]
        h0 = torch.tanh(self.h0_proj(pooled))      # [B,H]
        c0 = torch.tanh(self.c0_proj(pooled))      # [B,H]
        return h0, c0

    def step(self, y_prev, x_t, h, c, H_enc, enc_mask):
        # y_prev:[B, Dy], x_t:[B, x_dim], h,c:[B,H]
        if self.use_attention:
            ctx, _ = self.attn(h, H_enc, enc_mask)    # [B,H]
            inp = torch.cat([y_prev, x_t, ctx], dim=-1)
        else:
            inp = torch.cat([y_prev, x_t], dim=-1)

        h, c = self.cell(inp, (h, c))
        y_t = self.out(self.drop(h))                  # [B, Dy]
        return y_t, h, c

    def forward(self, H_enc, enc_mask, X_dec, Y, teacher_forcing=1.0):
        """
        H_enc:[B,T,H] vom Encoder, enc_mask:[B,T]
        X_dec:[B,T,x_dim] (Step-Features für Decoder, meist deine X)
        Y:[B,T,y_dim] (Targets, fürs Teacher Forcing)
        """
        B, T, _ = X_dec.shape
        Dy = Y.size(-1)

        h, c = self.init_state_from_encoder(H_enc, enc_mask)
        y_prev = torch.zeros(B, Dy, device=H_enc.device)

        outs = []
        for t in range(T):
            x_t = X_dec[:, t, :]                    # [B,x_dim]
            y_t, h, c = self.step(y_prev, x_t, h, c, H_enc, enc_mask)
            outs.append(y_t)

            if t+1 < T:
                use_tf = torch.rand(()) < teacher_forcing
                y_prev = Y[:, t, :] if use_tf else y_t

        return torch.stack(outs, dim=1)  # [B,T,Dy]

    @torch.no_grad()
    def infer(self, H_enc, enc_mask, X_dec, Y_prefix=None, k=0):
        """
        Autoregressive Vorhersage.
          - Wenn k>0: erste k Ausgaben aus Y_prefix übernehmen (bekannte echte Werte),
            danach autoregressiv weiter.
        """
        B, T, _ = X_dec.shape
        Dy = (Y_prefix.size(-1) if (Y_prefix is not None) else 1)

        h, c = self.init_state_from_encoder(H_enc, enc_mask)
        y_prev = torch.zeros(B, Dy, device=H_enc.device)

        outs = []
        for t in range(T):
            x_t = X_dec[:, t, :]
            if Y_prefix is not None and t < k:
                y_t = Y_prefix[:, t, :]           # echte bekannten Werte einsetzen
                outs.append(y_t)
                y_prev = y_t
                continue

            y_t, h, c = self.step(y_prev, x_t, h, c, H_enc, enc_mask)
            outs.append(y_t)
            y_prev = y_t

        return torch.stack(outs, dim=1)  # [B,T,Dy]


class BiLSTMAttnEncoder(nn.Module):
    def __init__(self, x_dim, hid=128, attn_heads=4, dropout=0.1):
        super().__init__()
        self.bilstm = nn.LSTM(input_size=x_dim, hidden_size=hid//2,
                              num_layers=1, batch_first=True, bidirectional=True)
        self.attn = nn.MultiheadAttention(embed_dim=hid, num_heads=attn_heads, batch_first=True)
        self.ln1 = nn.LayerNorm(hid)
        self.ff = nn.Sequential(
            nn.Linear(hid, hid*2), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(hid*2, hid)
        )
        self.ln2 = nn.LayerNorm(hid)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # x: [B,T,x_dim]; mask: [B,T] (1=real, 0=pad) -> key_padding_mask braucht True=pad
        h, _ = self.bilstm(x)                        # [B,T,hid]
        kpm = None
        if mask is not None:
            kpm = ~(mask.bool())                     # True an Padding-Positionen
        h_attn, _ = self.attn(h, h, h, key_padding_mask=kpm)
        h = self.ln1(h + self.dropout(h_attn))       # Residual + LN
        h_ff = self.ff(h)
        h = self.ln2(h + self.dropout(h_ff))         # Residual + LN
        return h

