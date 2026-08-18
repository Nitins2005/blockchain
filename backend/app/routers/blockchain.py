from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta

router = APIRouter()

class BlockchainConfigUpdate(BaseModel):
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: Optional[bool] = None

_blockchain_configs = {
    "bitcoin": {
        "id": 1, "blockchain": "bitcoin", "display_name": "Bitcoin",
        "api_url": "https://blockstream.info/api", "api_key_encrypted": "",
        "is_enabled": True, "last_sync": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        "tx_count": 125430, "wallet_count": 45210, "block_height": 850123, "sync_status": "synced"
    },
    "ethereum": {
        "id": 2, "blockchain": "ethereum", "display_name": "Ethereum",
        "api_url": "https://api.etherscan.io/api", "api_key_encrypted": "",
        "is_enabled": True, "last_sync": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        "tx_count": 284920, "wallet_count": 98450, "block_height": 20500123, "sync_status": "synced"
    },
    "bnb": {
        "id": 3, "blockchain": "bnb", "display_name": "BNB Chain",
        "api_url": "https://api.bscscan.com/api", "api_key_encrypted": "",
        "is_enabled": True, "last_sync": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
        "tx_count": 98120, "wallet_count": 34200, "block_height": 41000000, "sync_status": "synced"
    },
    "polygon": {
        "id": 4, "blockchain": "polygon", "display_name": "Polygon",
        "api_url": "https://api.polygonscan.com/api", "api_key_encrypted": "",
        "is_enabled": True, "last_sync": (datetime.utcnow() - timedelta(minutes=45)).isoformat(),
        "tx_count": 56780, "wallet_count": 22100, "block_height": 58000000, "sync_status": "synced"
    },
    "tron": {
        "id": 5, "blockchain": "tron", "display_name": "Tron",
        "api_url": "https://api.trongrid.io", "api_key_encrypted": "",
        "is_enabled": False, "last_sync": (datetime.utcnow() - timedelta(hours=24)).isoformat(),
        "tx_count": 23450, "wallet_count": 9800, "block_height": 63000000, "sync_status": "idle"
    }
}

@router.get("/configs")
async def get_configs():
    return list(_blockchain_configs.values())

@router.get("/status")
async def get_status():
    return list(_blockchain_configs.values())

@router.put("/configs/{chain}")
async def update_config(chain: str, data: BlockchainConfigUpdate):
    if chain not in _blockchain_configs:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Blockchain not found")
    cfg = _blockchain_configs[chain]
    if data.api_url is not None:
        cfg["api_url"] = data.api_url
    if data.api_key is not None:
        cfg["api_key_encrypted"] = "***" + data.api_key[-4:] if len(data.api_key) > 4 else "***"
    if data.is_enabled is not None:
        cfg["is_enabled"] = data.is_enabled
        cfg["sync_status"] = "idle" if not data.is_enabled else cfg["sync_status"]
    return cfg

@router.post("/sync/{chain}")
async def sync_blockchain(chain: str):
    if chain not in _blockchain_configs:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Blockchain not found")
    cfg = _blockchain_configs[chain]
    cfg["sync_status"] = "syncing"
    # Simulate sync result
    cfg["tx_count"] += random.randint(100, 5000)
    cfg["wallet_count"] += random.randint(10, 500)
    cfg["block_height"] += random.randint(10, 500)
    cfg["last_sync"] = datetime.utcnow().isoformat()
    cfg["sync_status"] = "synced"
    return {"message": f"Sync completed for {chain}", "config": cfg}
