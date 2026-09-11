import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.services.graph_service import (
    _compute_basic_features,
    _compute_graph_features,
    _blockchain_to_id,
    get_feature_vector,
    FEATURE_NAMES,
)
from app.models.wallet_feature import WalletFeature


class MockTransaction:
    def __init__(self, sender=None, receiver=None, amount=1.0, gas_fee=0.001,
                 token="ETH", blockchain="ethereum", timestamp=None, status="confirmed"):
        self.sender_address = sender
        self.receiver_address = receiver
        self.amount = amount
        self.gas_fee = gas_fee
        self.token = token
        self.blockchain = blockchain
        self.timestamp = timestamp or datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.status = status


class TestBasicFeatures:
    def test_empty_transactions(self):
        result = _compute_basic_features([])
        assert result["incoming_tx"] == 0
        assert result["outgoing_tx"] == 0
        assert result["avg_tx_amount"] == 0.0
        assert result["max_tx_amount"] == 0.0
        assert result["active_days"] == 0
        assert result["gas_usage"] == 0.0
        assert result["token_diversity"] == 1

    def test_single_outgoing(self):
        tx = MockTransaction(sender="0xAAA", receiver="0xBBB", amount=5.0, gas_fee=0.01)
        result = _compute_basic_features([tx])
        assert result["outgoing_tx"] == 1
        assert result["incoming_tx"] == 1
        assert result["avg_tx_amount"] == 5.0
        assert result["max_tx_amount"] == 5.0
        assert result["gas_usage"] == 0.01

    def test_multiple_txs_diversity(self):
        txs = [
            MockTransaction(sender="0xAAA", receiver="0xBBB", amount=1.0, token="ETH"),
            MockTransaction(sender="0xAAA", receiver="0xCCC", amount=2.0, token="USDC"),
            MockTransaction(sender="0xBBB", receiver="0xAAA", amount=0.5, token="ETH", blockchain="bnb"),
        ]
        result = _compute_basic_features(txs)
        assert result["token_diversity"] == 2
        assert result["avg_tx_amount"] == pytest.approx(1.166, abs=0.01)
        assert result["max_tx_amount"] == 2.0

    def test_active_days(self):
        ts1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        ts2 = datetime(2026, 1, 3, tzinfo=timezone.utc)
        txs = [
            MockTransaction(sender="0xA", receiver="0xB", timestamp=ts1),
            MockTransaction(sender="0xA", receiver="0xB", timestamp=ts2),
        ]
        result = _compute_basic_features(txs)
        assert result["active_days"] == 2


class TestGraphFeatures:
    def test_no_neo4j(self):
        with patch("app.services.graph_service.neo4j_client") as mock:
            mock.is_connected = False
            result = _compute_graph_features("0xtest")
            assert result["neighbor_count"] == 0
            assert result["degree_centrality"] == 0.0


class TestBlockchainId:
    def test_known_chains(self):
        assert _blockchain_to_id("ethereum") == 1
        assert _blockchain_to_id("bitcoin") == 0
        assert _blockchain_to_id("bnb") == 2

    def test_unknown_chain(self):
        assert _blockchain_to_id("solana") == 1


class TestFeatureVector:
    def test_vector_length(self):
        wf = WalletFeature(
            id=1, wallet_address="0xtest", blockchain="ethereum",
            incoming_tx=10, outgoing_tx=5, avg_tx_amount=1.5, max_tx_amount=10.0,
            balance=5.0, active_days=30, gas_usage=0.5, token_diversity=3,
            neighbor_count=20, degree_centrality=0.02, betweenness_centrality=0.01,
            pagerank=0.005, clustering_coefficient=0.4, cross_chain_tx_count=2,
        )
        result = get_feature_vector(wf)
        assert len(result["feature_values"]) == len(FEATURE_NAMES)
        assert result["wallet_address"] == "0xtest"
        assert result["feature_names"] == FEATURE_NAMES

    def test_vector_values(self):
        wf = WalletFeature(
            id=1, wallet_address="0xtest", blockchain="ethereum",
            incoming_tx=100, outgoing_tx=50, avg_tx_amount=2.5, max_tx_amount=50.0,
            balance=100.0, active_days=60, gas_usage=1.2, token_diversity=5,
            neighbor_count=30, degree_centrality=0.03, betweenness_centrality=0.02,
            pagerank=0.008, clustering_coefficient=0.5, cross_chain_tx_count=3,
        )
        result = get_feature_vector(wf)
        assert result["feature_values"][0] == 100.0
        assert result["feature_values"][1] == 50.0
        assert result["feature_values"][4] == 100.0


class TestFeatureNames:
    def test_all_names_present(self):
        assert len(FEATURE_NAMES) == 14
        assert "pagerank" in FEATURE_NAMES
        assert "degree_centrality" in FEATURE_NAMES
        assert "clustering_coefficient" in FEATURE_NAMES
