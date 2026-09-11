import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from app.blockchain.base import NormalizedTransaction, BlockchainSyncResult
from app.blockchain.ethereum import EthereumAdapter
from app.blockchain.bsc import BSCAdapter
from app.blockchain.normalizer import store_transactions, store_wallets
from app.blockchain.graph_builder import build_graph_from_transactions


def _make_mock_tx(
    tx_hash="0xabc123",
    sender="0xsender",
    receiver="0xreceiver",
    blockchain="ethereum",
    amount=1.5,
):
    return NormalizedTransaction(
        tx_hash=tx_hash,
        sender_address=sender.lower(),
        receiver_address=receiver.lower(),
        blockchain=blockchain,
        amount=amount,
        amount_usd=None,
        gas_fee=0.001,
        gas_fee_usd=None,
        token="ETH",
        block_number=12345,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        status="confirmed",
    )


class TestNormalizedTransaction:
    def test_create(self):
        tx = _make_mock_tx()
        assert tx.tx_hash == "0xabc123"
        assert tx.blockchain == "ethereum"
        assert tx.amount == 1.5
        assert tx.status == "confirmed"

    def test_defaults(self):
        tx = _make_mock_tx()
        assert tx.is_flagged is False
        assert tx.amount_usd is None


class TestEthereumAdapter:
    def test_chain_name(self):
        adapter = EthereumAdapter(api_key="test")
        assert adapter.chain_name == "ethereum"

    def test_native_token(self):
        adapter = EthereumAdapter(api_key="test")
        assert adapter.native_token == "ETH"

    def test_parse_tx(self):
        adapter = EthereumAdapter(api_key="test")
        raw = {
            "hash": "0xdef456",
            "from": "0xSENDER",
            "to": "0xRECEIVER",
            "value": "1500000000000000000",
            "gasUsed": "21000",
            "gasPrice": "20000000000",
            "timeStamp": "1700000000",
            "blockNumber": "20000000",
            "txreceipt_status": "1",
        }
        tx = adapter._parse_tx(raw)
        assert tx.tx_hash == "0xdef456"
        assert tx.sender_address == "0xsender"
        assert tx.receiver_address == "0xreceiver"
        assert tx.amount == pytest.approx(1.5, abs=0.01)
        assert tx.blockchain == "ethereum"
        assert tx.status == "confirmed"


class TestBSCAdapter:
    def test_chain_name(self):
        adapter = BSCAdapter(api_key="test")
        assert adapter.chain_name == "bnb"

    def test_native_token(self):
        adapter = BSCAdapter(api_key="test")
        assert adapter.native_token == "BNB"

    def test_parse_tx_overrides_blockchain(self):
        adapter = BSCAdapter(api_key="test")
        raw = {
            "hash": "0xghi789",
            "from": "0xSENDER",
            "to": "0xRECEIVER",
            "value": "1000000000000000000",
            "gasUsed": "21000",
            "gasPrice": "5000000000",
            "timeStamp": "1700000000",
            "blockNumber": "40000000",
            "txreceipt_status": "1",
        }
        tx = adapter._parse_tx(raw)
        assert tx.blockchain == "bnb"
        assert tx.token == "BNB"


@pytest.mark.asyncio
async def test_store_transactions(db_session):
    txs = [
        _make_mock_tx(tx_hash="0xunique1"),
        _make_mock_tx(tx_hash="0xunique2"),
    ]
    stored = await store_transactions(db_session, txs)
    assert stored == 2

    stored_again = await store_transactions(db_session, txs)
    assert stored_again == 0


@pytest.mark.asyncio
async def test_store_wallets(db_session):
    txs = [
        _make_mock_tx(sender="0xAAAA", receiver="0xBBBB"),
    ]
    stored = await store_wallets(db_session, txs, "ethereum")
    assert stored == 2


class TestGraphBuilder:
    def test_build_graph_no_neo4j(self):
        result = build_graph_from_transactions([])
        assert result == {"wallets_created": 0, "edges_created": 0}

    def test_build_graph_with_txs(self):
        txs = [
            _make_mock_tx(tx_hash="0xtx1", sender="0xAAA", receiver="0xBBB"),
            _make_mock_tx(tx_hash="0xtx2", sender="0xBBB", receiver="0xCCC"),
        ]
        with patch("app.blockchain.graph_builder.neo4j_client") as mock_neo4j:
            mock_neo4j.is_connected = True
            mock_neo4j.create_wallet_node.return_value = None
            mock_neo4j.create_transaction_edge.return_value = None
            result = build_graph_from_transactions(txs)
            assert result["edges_created"] == 2
            assert mock_neo4j.create_wallet_node.call_count == 4
