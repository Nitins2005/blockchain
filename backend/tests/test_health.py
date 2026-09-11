import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CryptoShield AI"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "CryptoShield" in data["message"]


@pytest.mark.asyncio
async def test_docs_endpoint(client):
    response = await client.get("/docs")
    assert response.status_code == 200
