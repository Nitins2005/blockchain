from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta
from app.services.mock_data_service import generate_mock_wallets, generate_mock_transactions, generate_wallet_address, BLOCKCHAINS

router = APIRouter()

class WalletCreate(BaseModel):
    address: str
    blockchain: str
    label: Optional[str] = None

_wallets_store = generate_mock_wallets(100)

@router.get("")
async def list_wallets(
    page: int = 1, page_size: int = 20,
    blockchain: Optional[str] = None, risk_level: Optional[str] = None,
    search: Optional[str] = None, is_blacklisted: Optional[bool] = None
):
    items = _wallets_store.copy()
    if blockchain:
        items = [w for w in items if w["blockchain"] == blockchain]
    if risk_level:
        items = [w for w in items if w.get("risk_level") == risk_level]
    if search:
        items = [w for w in items if search.lower() in w["address"].lower()]
    if is_blacklisted is not None:
        items = [w for w in items if w["is_blacklisted"] == is_blacklisted]
    total = len(items)
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "total": total, "page": page, "page_size": page_size}

@router.get("/{address}")
async def get_wallet(address: str):
    for w in _wallets_store:
        if w["address"].lower() == address.lower():
            return w
    # Return a dynamic mock for any address
    blockchain = random.choice(BLOCKCHAINS)
    return {
        "id": random.randint(1000, 9999), "address": address, "blockchain": blockchain,
        "tx_count": random.randint(5, 5000), "balance": round(random.uniform(0, 1000), 6),
        "fraud_score": round(random.uniform(0.1, 0.9), 4),
        "risk_level": random.choice(["low", "medium", "high", "critical"]),
        "category": random.choice(["Exchange", "Personal Wallet", "Unknown", "DeFi Protocol"]),
        "is_blacklisted": False,
        "last_active": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat()
    }

@router.get("/{address}/transactions")
async def get_wallet_transactions(address: str, page: int = 1, page_size: int = 20):
    data = generate_mock_transactions(count=50, page=page, page_size=page_size)
    for tx in data["items"]:
        if random.random() > 0.5:
            tx["sender_address"] = address
        else:
            tx["receiver_address"] = address
    return data

@router.post("")
async def create_wallet(data: WalletCreate):
    new_id = max(w["id"] for w in _wallets_store) + 1
    wallet = {
        "id": new_id, "address": data.address, "blockchain": data.blockchain,
        "label": data.label, "tx_count": 0, "balance": 0.0,
        "fraud_score": None, "risk_level": None, "category": None,
        "is_blacklisted": False,
        "last_active": None
    }
    _wallets_store.append(wallet)
    return wallet

@router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: int):
    global _wallets_store
    _wallets_store = [w for w in _wallets_store if w["id"] != wallet_id]
    return {"message": "Wallet deleted"}
