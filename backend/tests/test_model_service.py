import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock
from app.models.gnn_model import TemporalGNN, GCNLayer, TemporalAttention, WalletAttributionModel
from app.services.model_service import (
    state, predict_fraud, predict_attribution, generate_explanation,
    _init_models, _features_to_tensor, WALLET_CATEGORIES, FRAUD_LABELS,
    train_models,
)
from app.services.graph_service import FEATURE_NAMES


class TestTemporalGNN:
    def test_init(self):
        model = TemporalGNN(in_features=14)
        assert model.in_features == 14
        assert model.hidden_dim == 64
        assert model.num_layers == 3

    def test_forward_no_edges(self):
        model = TemporalGNN(in_features=14)
        model.eval()
        x = torch.randn(1, 14)
        with torch.no_grad():
            out = model(x)
        assert "fraud_score" in out
        assert "attribution_logits" in out
        assert "embeddings" in out
        assert out["fraud_score"].shape == (1,)
        assert out["attribution_logits"].shape == (1, 8)

    def test_forward_batch(self):
        model = TemporalGNN(in_features=14)
        model.eval()
        x = torch.randn(8, 14)
        with torch.no_grad():
            out = model(x)
        assert out["fraud_score"].shape == (8,)
        assert out["attribution_logits"].shape == (8, 8)

    def test_forward_with_edges(self):
        model = TemporalGNN(in_features=14)
        model.eval()
        x = torch.randn(4, 14)
        edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]])
        with torch.no_grad():
            out = model(x, edge_index)
        assert out["fraud_score"].shape == (4,)


class TestGCNLayer:
    def test_forward_no_edges(self):
        layer = GCNLayer(14, 32)
        x = torch.randn(4, 14)
        out = layer(x, None)
        assert out.shape == (4, 32)

    def test_forward_with_edges(self):
        layer = GCNLayer(14, 32)
        x = torch.randn(4, 14)
        edge_index = torch.tensor([[0, 1], [1, 0]])
        out = layer(x, edge_index)
        assert out.shape == (4, 32)


class TestTemporalAttention:
    def test_forward(self):
        attn = TemporalAttention(64)
        x = torch.randn(4, 64)
        out = attn(x)
        assert out.shape == (4, 64)


class TestWalletAttributionModel:
    def test_forward(self):
        model = WalletAttributionModel(in_features=14)
        x = torch.randn(1, 14)
        out = model(x)
        assert out.shape == (1, 8)

    def test_forward_batch(self):
        model = WalletAttributionModel(in_features=14)
        x = torch.randn(16, 14)
        out = model(x)
        assert out.shape == (16, 8)


class TestModelService:
    def test_init_models(self):
        _init_models()
        assert state.fraud_model is not None
        assert state.attribution_model is not None
        assert isinstance(state.fraud_model, TemporalGNN)

    def test_features_to_tensor(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0]
        t = _features_to_tensor(values)
        assert t.shape == (1, 14)
        assert t.dtype == torch.float32

    def test_predict_fraud(self):
        _init_models()
        features = list(range(14))
        features = [float(f) for f in features]
        pred = predict_fraud(features)
        assert "fraud_score" in pred
        assert "risk_level" in pred
        assert "confidence" in pred
        assert "model_version" in pred
        assert pred["risk_level"] in ("low", "medium", "high", "critical")
        assert 0.0 <= pred["fraud_score"] <= 1.0

    def test_predict_attribution(self):
        _init_models()
        features = [float(i) for i in range(14)]
        pred = predict_attribution(features)
        assert "category" in pred
        assert "confidence" in pred
        assert pred["category"] in WALLET_CATEGORIES
        assert 0.0 <= pred["confidence"] <= 1.0

    def test_generate_explanation(self):
        _init_models()
        features = [float(i) for i in range(14)]
        explanation = generate_explanation(features, FEATURE_NAMES, "0xtest")
        assert "wallet_address" in explanation
        assert "top_features" in explanation
        assert "risk_factors" in explanation
        assert "reasoning_text" in explanation
        assert "fraud_score" in explanation
        assert len(explanation["top_features"]) <= 6
        assert len(explanation["risk_factors"]) >= 1

    def test_train_models(self):
        _init_models()
        X = [[float(i) for i in range(14)] for _ in range(50)]
        fraud_labels = [0] * 40 + [1] * 10
        attr_labels = [0] * 25 + [1] * 25
        result = train_models(X, fraud_labels, attr_labels, epochs=3, batch_size=16)
        assert result["status"] == "completed"
        assert result["epochs_completed"] == 3
        assert "metrics" in result
        assert state.model_version != "untrained"

    def test_state_properties(self):
        assert hasattr(state, "fraud_model")
        assert hasattr(state, "is_training")
        assert hasattr(state, "training_progress")


class TestConstants:
    def test_wallet_categories(self):
        assert len(WALLET_CATEGORIES) == 8
        assert "scam" in WALLET_CATEGORIES
        assert "exchange" in WALLET_CATEGORIES

    def test_fraud_labels(self):
        assert len(FRAUD_LABELS) == 4
        assert FRAUD_LABELS[0] == "low"
        assert FRAUD_LABELS[3] == "critical"

    def test_feature_names_count(self):
        assert len(FEATURE_NAMES) == 14
