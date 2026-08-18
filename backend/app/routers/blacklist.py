from fastapi import APIRouter, HTTPException, UploadFile, File, Response
from pydantic import BaseModel
from typing import Optional, List
import random
from datetime import datetime, timedelta
from app.services.mock_data_service import BLOCKCHAINS, generate_wallet_address
from app.utils.csv_handler import generate_csv, parse_csv

router = APIRouter()

class BlacklistCreate(BaseModel):
    address: str
    blockchain: str
    category: str
    reason: Optional[str] = None
    source: Optional[str] = None
    confidence: str = "high"

class BlacklistUpdate(BaseModel):
    reason: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

# In-memory store for demo
_blacklist_store = []

def _seed_blacklist():
    if not _blacklist_store:
        categories = ["scam", "mixer", "exchange", "darknet", "other"]
        for i in range(50):
            blockchain = random.choice(BLOCKCHAINS)
            _blacklist_store.append({
                "id": i + 1,
                "address": generate_wallet_address(blockchain),
                "blockchain": blockchain,
                "category": random.choice(categories),
                "reason": random.choice([
                    "Involved in ransomware payments",
                    "Known mixer service",
                    "Darknet marketplace",
                    "Phishing campaign",
                    "Rug pull scheme"
                ]),
                "source": random.choice(["CryptoShield Internal", "Chainalysis", "OFAC", "Community Report"]),
                "confidence": random.choice(["high", "medium", "low"]),
                "is_active": True,
                "added_by": "admin",
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat()
            })

_seed_blacklist()

@router.get("")
async def get_blacklist(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    blockchain: Optional[str] = None,
    search: Optional[str] = None
):
    items = _blacklist_store.copy()
    if category:
        items = [i for i in items if i["category"] == category]
    if blockchain:
        items = [i for i in items if i["blockchain"] == blockchain]
    if search:
        items = [i for i in items if search.lower() in i["address"].lower()]
    total = len(items)
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "total": total, "page": page, "page_size": page_size}

@router.get("/check/{address}")
async def check_blacklist(address: str):
    for item in _blacklist_store:
        if item["address"].lower() == address.lower():
            return {"is_blacklisted": True, "entry": item}
    return {"is_blacklisted": False, "entry": None}

@router.get("/export")
async def export_blacklist():
    csv_data = generate_csv(_blacklist_store)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=blacklist.csv"}
    )

@router.get("/{entry_id}")
async def get_blacklist_entry(entry_id: int):
    for item in _blacklist_store:
        if item["id"] == entry_id:
            return item
    raise HTTPException(status_code=404, detail="Entry not found")

@router.post("")
async def create_blacklist_entry(data: BlacklistCreate):
    new_id = max((i["id"] for i in _blacklist_store), default=0) + 1
    entry = {
        "id": new_id,
        "address": data.address,
        "blockchain": data.blockchain,
        "category": data.category,
        "reason": data.reason,
        "source": data.source,
        "confidence": data.confidence,
        "is_active": True,
        "added_by": "current_user",
        "created_at": datetime.utcnow().isoformat()
    }
    _blacklist_store.append(entry)
    return entry

@router.put("/{entry_id}")
async def update_blacklist_entry(entry_id: int, data: BlacklistUpdate):
    for item in _blacklist_store:
        if item["id"] == entry_id:
            if data.reason is not None:
                item["reason"] = data.reason
            if data.category is not None:
                item["category"] = data.category
            if data.is_active is not None:
                item["is_active"] = data.is_active
            return item
    raise HTTPException(status_code=404, detail="Entry not found")

@router.delete("/{entry_id}")
async def delete_blacklist_entry(entry_id: int):
    global _blacklist_store
    _blacklist_store = [i for i in _blacklist_store if i["id"] != entry_id]
    return {"message": "Entry deleted"}

@router.post("/import")
async def import_blacklist(file: UploadFile = File(...)):
    content = await file.read()
    rows = parse_csv(content)
    imported = 0
    for row in rows:
        if "address" in row and "blockchain" in row:
            new_id = max((i["id"] for i in _blacklist_store), default=0) + 1
            _blacklist_store.append({
                "id": new_id,
                "address": row["address"],
                "blockchain": row.get("blockchain", "unknown"),
                "category": row.get("category", "other"),
                "reason": row.get("reason", ""),
                "source": row.get("source", "CSV Import"),
                "confidence": row.get("confidence", "medium"),
                "is_active": True,
                "added_by": "import",
                "created_at": datetime.utcnow().isoformat()
            })
            imported += 1
    return {"imported": imported, "message": f"Successfully imported {imported} entries"}
