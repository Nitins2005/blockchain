import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone


class TestAdminRouter:
    @pytest.mark.asyncio
    async def test_stats_empty_db(self, client):
        resp = await client.get("/api/admin/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_wallets" in data
        assert "total_transactions" in data
        assert "neo4j_connected" in data
        assert "model_status" in data

    @pytest.mark.asyncio
    async def test_fraud_trend(self, client):
        resp = await client.get("/api/admin/fraud-trend")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 30

    @pytest.mark.asyncio
    async def test_volume_trend(self, client):
        resp = await client.get("/api/admin/volume-trend")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 14

    @pytest.mark.asyncio
    async def test_blockchain_distribution(self, client):
        resp = await client.get("/api/admin/blockchain-distribution")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_system_health(self, client):
        resp = await client.get("/api/admin/system-health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["api_status"] == "operational"


class TestFraudRouter:
    @pytest.mark.asyncio
    async def test_high_risk_empty(self, client):
        resp = await client.get("/api/fraud/high-risk")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_fraud_stats(self, client):
        resp = await client.get("/api/fraud/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_analyzed" in data
        assert "high_risk_count" in data

    @pytest.mark.asyncio
    async def test_prediction_history(self, client):
        resp = await client.get("/api/fraud/history/0xtest123")
        assert resp.status_code == 200
        data = resp.json()
        assert data["address"] == "0xtest123"
        assert "history" in data


class TestWalletsRouter:
    @pytest.mark.asyncio
    async def test_list_wallets_empty(self, client):
        resp = await client.get("/api/wallets")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_wallet_not_found(self, client):
        resp = await client.get("/api/wallets/0xnonexistent")
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_create_wallet(self, client):
        resp = await client.post("/api/wallets", json={
            "address": "0x1234567890abcdef1234567890abcdef12345678",
            "blockchain": "ethereum",
            "label": "Test Wallet",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["address"] == "0x1234567890abcdef1234567890abcdef12345678"
        assert data["blockchain"] == "ethereum"

    @pytest.mark.asyncio
    async def test_create_wallet_duplicate(self, client):
        await client.post("/api/wallets", json={
            "address": "0xabcdef",
            "blockchain": "ethereum",
        })
        resp = await client.post("/api/wallets", json={
            "address": "0xabcdef",
            "blockchain": "ethereum",
        })
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_wallet_transactions_empty(self, client):
        resp = await client.get("/api/wallets/0xtest/transactions")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_delete_wallet_not_found(self, client):
        resp = await client.delete("/api/wallets/99999")
        assert resp.status_code == 404
