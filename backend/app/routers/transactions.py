from fastapi import APIRouter, UploadFile, File, Response
from typing import Optional
import random
from datetime import datetime
from app.services.mock_data_service import generate_mock_transactions, BLOCKCHAINS, TOKENS
from app.utils.csv_handler import generate_csv, parse_csv

router = APIRouter()

@router.get("")
async def list_transactions(
    page: int = 1, page_size: int = 20,
    blockchain: Optional[str] = None, status: Optional[str] = None,
    token: Optional[str] = None, search: Optional[str] = None,
    is_flagged: Optional[bool] = None
):
    data = generate_mock_transactions(count=200, page=page, page_size=page_size)
    if blockchain:
        data["items"] = [t for t in data["items"] if t["blockchain"] == blockchain]
    if status:
        data["items"] = [t for t in data["items"] if t["status"] == status]
    if token:
        data["items"] = [t for t in data["items"] if t["token"] == token]
    if search:
        data["items"] = [t for t in data["items"]
                          if search.lower() in t["tx_hash"].lower()
                          or search.lower() in t["sender_address"].lower()
                          or search.lower() in t["receiver_address"].lower()]
    if is_flagged is not None:
        data["items"] = [t for t in data["items"] if t["is_flagged"] == is_flagged]
    return data

@router.get("/export")
async def export_transactions():
    data = generate_mock_transactions(count=100, page=1, page_size=100)
    csv_bytes = generate_csv(data["items"])
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )

@router.get("/{tx_hash}")
async def get_transaction(tx_hash: str):
    blockchain = random.choice(BLOCKCHAINS)
    amount = round(random.uniform(0.001, 10000), 6)
    return {
        "id": random.randint(1, 99999),
        "tx_hash": tx_hash,
        "sender_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
        "receiver_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
        "blockchain": blockchain,
        "amount": amount,
        "amount_usd": round(amount * random.uniform(100, 50000), 2),
        "gas_fee": round(random.uniform(0.00001, 0.01), 8),
        "token": random.choice(TOKENS),
        "block_number": random.randint(1000000, 50000000),
        "timestamp": datetime.utcnow().isoformat(),
        "status": "confirmed",
        "is_flagged": random.random() > 0.8
    }

@router.post("/upload")
async def upload_transactions(file: UploadFile = File(...)):
    content = await file.read()
    rows = parse_csv(content)
    return {"imported": len(rows), "message": f"Successfully processed {len(rows)} transactions from CSV"}
