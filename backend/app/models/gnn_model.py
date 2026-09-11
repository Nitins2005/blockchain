import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class TemporalGNN(nn.Module):
    """Temporal Graph Neural Network for fraud detection and wallet attribution.

    Architecture:
    - Input: node feature matrix (batch_size, num_features)
    - GCN layers for spatial aggregation
    - Temporal attention for time-series patterns
    - Dual-head output: fraud_score + attribution category
    """

    def __init__(
        self,
        in_features: int = 14,
        hidden_dim: int = 64,
        num_layers: int = 3,
        dropout: float = 0.3,
        num_attribution_classes: int = 8,
    ):
        super().__init__()
        self.in_features = in_features
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_attribution_classes = num_attribution_classes

        self.input_proj = nn.Linear(in_features, hidden_dim)

        self.gcn_layers = nn.ModuleList()
        self.layer_norms = nn.ModuleList()
        for _ in range(num_layers):
            self.gcn_layers.append(GCNLayer(hidden_dim, hidden_dim))
            self.layer_norms.append(nn.LayerNorm(hidden_dim))

        self.temporal_attention = TemporalAttention(hidden_dim)

        self.fraud_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid(),
        )

        self.attribution_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_attribution_classes),
        )

        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: Optional[torch.Tensor] = None,
        batch: Optional[torch.Tensor] = None,
    ) -> dict:
        h = self.input_proj(x)
        h = F.relu(h)
        h = self.dropout(h)

        for gcn, ln in zip(self.gcn_layers, self.layer_norms):
            residual = h
            h_new = gcn(h, edge_index)
            h_new = ln(h_new + residual)
            h_new = F.relu(h_new)
            h_new = self.dropout(h_new)
            h = h_new

        h = self.temporal_attention(h)

        fraud_score = self.fraud_head(h).squeeze(-1)
        attribution_logits = self.attribution_head(h)

        return {
            "fraud_score": fraud_score,
            "attribution_logits": attribution_logits,
            "embeddings": h,
        }


class GCNLayer(nn.Module):
    """Simple GCN layer with symmetric normalization."""

    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.weight = nn.Linear(in_features, out_features, bias=False)
        self.bias = nn.Parameter(torch.zeros(out_features))

    def forward(self, x: torch.Tensor, edge_index: Optional[torch.Tensor] = None) -> torch.Tensor:
        if edge_index is None:
            return self.weight(x) + self.bias

        row, col = edge_index
        deg = torch.zeros(x.size(0), device=x.device)
        deg.scatter_add_(0, row, torch.ones(row.size(0), device=x.device))
        deg = deg.clamp(min=1)
        norm = 1.0 / deg

        h = self.weight(x)
        h = h[row] * norm[row].unsqueeze(-1)
        out = torch.zeros(x.size(0), h.size(1), device=x.device, dtype=x.dtype)
        out.scatter_add_(0, col.unsqueeze(-1).expand_as(h), h)
        out = out + self.bias
        return out


class TemporalAttention(nn.Module):
    """Attention mechanism over node features for temporal patterns."""

    def __init__(self, hidden_dim: int):
        super().__init__()
        self.query = nn.Linear(hidden_dim, hidden_dim)
        self.key = nn.Linear(hidden_dim, hidden_dim)
        self.value = nn.Linear(hidden_dim, hidden_dim)
        self.scale = hidden_dim ** 0.5

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        q = self.query(x)
        k = self.key(x)
        v = self.value(x)

        attn = torch.matmul(q, k.transpose(-2, -1)) / self.scale
        attn = F.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)
        return out + x


class WalletAttributionModel(nn.Module):
    """Lightweight MLP for wallet category classification (standalone)."""

    def __init__(self, in_features: int = 14, hidden_dim: int = 32, num_classes: int = 8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
