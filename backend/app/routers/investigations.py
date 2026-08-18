from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
from datetime import datetime, timedelta
from app.services.mock_data_service import generate_wallet_address, BLOCKCHAINS

router = APIRouter()

class InvestigationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assigned_to_id: Optional[int] = None

class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[int] = None

class NoteCreate(BaseModel):
    content: str

class WalletAttach(BaseModel):
    wallet_address: str
    blockchain: str

# In-memory store
_investigations = []
_notes = {}
_wallets = {}

def _seed_investigations():
    if not _investigations:
        statuses = ["open", "in_progress", "closed"]
        priorities = ["critical", "high", "medium", "low"]
        titles = [
            "Ponzi Scheme Investigation", "Darknet Market Analysis",
            "Ransomware Payment Tracking", "Mixer Usage Detection",
            "Exchange Hack Follow-up", "DeFi Protocol Exploit",
            "NFT Wash Trading", "Cross-chain Bridge Fraud",
            "Phishing Campaign Wallets", "Money Laundering Ring"
        ]
        for i, title in enumerate(titles):
            inv_id = i + 1
            _investigations.append({
                "id": inv_id,
                "title": title,
                "description": f"Detailed investigation of {title.lower()}",
                "status": random.choice(statuses),
                "priority": random.choice(priorities),
                "created_by_id": 1,
                "assigned_to_id": random.randint(1, 5),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            })
            blockchain = random.choice(BLOCKCHAINS)
            _wallets[inv_id] = [
                {"id": j+1, "investigation_id": inv_id,
                 "wallet_address": generate_wallet_address(blockchain),
                 "blockchain": blockchain,
                 "added_at": datetime.utcnow().isoformat()}
                for j in range(random.randint(1, 5))
            ]
            _notes[inv_id] = [
                {"id": j+1, "investigation_id": inv_id,
                 "content": random.choice([
                     "Initial analysis shows suspicious patterns.",
                     "Cross-chain movement detected. Expanding scope.",
                     "Blacklisted wallet found in transaction graph.",
                     "Coordinating with exchange for KYC data."
                 ]),
                 "author_id": 1,
                 "created_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 72))).isoformat()}
                for j in range(random.randint(1, 4))
            ]

_seed_investigations()

@router.get("")
async def list_investigations(
    page: int = 1, page_size: int = 20,
    status: Optional[str] = None, priority: Optional[str] = None
):
    items = _investigations.copy()
    if status:
        items = [i for i in items if i["status"] == status]
    if priority:
        items = [i for i in items if i["priority"] == priority]
    total = len(items)
    start = (page - 1) * page_size
    page_items = items[start:start + page_size]
    for item in page_items:
        item["wallet_count"] = len(_wallets.get(item["id"], []))
    return {"items": page_items, "total": total, "page": page, "page_size": page_size}

@router.get("/{inv_id}")
async def get_investigation(inv_id: int):
    for item in _investigations:
        if item["id"] == inv_id:
            item["wallet_count"] = len(_wallets.get(inv_id, []))
            return item
    raise HTTPException(status_code=404, detail="Investigation not found")

@router.post("")
async def create_investigation(data: InvestigationCreate):
    new_id = max((i["id"] for i in _investigations), default=0) + 1
    inv = {
        "id": new_id, "title": data.title, "description": data.description,
        "status": "open", "priority": data.priority,
        "created_by_id": 1, "assigned_to_id": data.assigned_to_id,
        "created_at": datetime.utcnow().isoformat(), "updated_at": datetime.utcnow().isoformat()
    }
    _investigations.append(inv)
    _wallets[new_id] = []
    _notes[new_id] = []
    return inv

@router.put("/{inv_id}")
async def update_investigation(inv_id: int, data: InvestigationUpdate):
    for item in _investigations:
        if item["id"] == inv_id:
            if data.title is not None: item["title"] = data.title
            if data.description is not None: item["description"] = data.description
            if data.status is not None: item["status"] = data.status
            if data.priority is not None: item["priority"] = data.priority
            if data.assigned_to_id is not None: item["assigned_to_id"] = data.assigned_to_id
            item["updated_at"] = datetime.utcnow().isoformat()
            return item
    raise HTTPException(status_code=404, detail="Investigation not found")

@router.delete("/{inv_id}")
async def delete_investigation(inv_id: int):
    global _investigations
    _investigations = [i for i in _investigations if i["id"] != inv_id]
    _wallets.pop(inv_id, None)
    _notes.pop(inv_id, None)
    return {"message": "Investigation deleted"}

@router.get("/{inv_id}/wallets")
async def get_investigation_wallets(inv_id: int):
    return _wallets.get(inv_id, [])

@router.post("/{inv_id}/wallets")
async def attach_wallet(inv_id: int, data: WalletAttach):
    if inv_id not in _wallets:
        _wallets[inv_id] = []
    new_id = len(_wallets[inv_id]) + 1
    entry = {"id": new_id, "investigation_id": inv_id,
              "wallet_address": data.wallet_address, "blockchain": data.blockchain,
              "added_at": datetime.utcnow().isoformat()}
    _wallets[inv_id].append(entry)
    return entry

@router.delete("/{inv_id}/wallets/{wallet_address}")
async def remove_wallet(inv_id: int, wallet_address: str):
    if inv_id in _wallets:
        _wallets[inv_id] = [w for w in _wallets[inv_id] if w["wallet_address"] != wallet_address]
    return {"message": "Wallet removed"}

@router.get("/{inv_id}/notes")
async def get_notes(inv_id: int):
    return _notes.get(inv_id, [])

@router.post("/{inv_id}/notes")
async def add_note(inv_id: int, data: NoteCreate):
    if inv_id not in _notes:
        _notes[inv_id] = []
    new_id = len(_notes[inv_id]) + 1
    note = {"id": new_id, "investigation_id": inv_id,
             "content": data.content, "author_id": 1,
             "created_at": datetime.utcnow().isoformat()}
    _notes[inv_id].append(note)
    return note

@router.post("/{inv_id}/generate-report")
async def generate_report(inv_id: int):
    return {"message": "Report generation started", "investigation_id": inv_id,
            "report_id": random.randint(100, 999), "eta_seconds": 5}
