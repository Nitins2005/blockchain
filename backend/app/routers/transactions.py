from fastapi import APIRouter, UploadFile, File, Response, Depends
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.transaction import Transaction
from app.utils.csv_handler import generate_csv, parse_csv

router = APIRouter()


@router.get("")
async def list_transactions(
    page: int = 1,
    page_size: int = 20,
    blockchain: Optional[str] = None,
    status: Optional[str] = None,
    token: Optional[str] = None,
    search: Optional[str] = None,
    is_flagged: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Transaction)
    count_query = select(func.count(Transaction.id))

    if blockchain:
        query = query.where(Transaction.blockchain == blockchain)
        count_query = count_query.where(Transaction.blockchain == blockchain)
    if status:
        query = query.where(Transaction.status == status)
        count_query = count_query.where(Transaction.status == status)
    if token:
        query = query.where(Transaction.token == token)
        count_query = count_query.where(Transaction.token == token)
    if is_flagged is not None:
        query = query.where(Transaction.is_flagged == is_flagged)
        count_query = count_query.where(Transaction.is_flagged == is_flagged)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            Transaction.tx_hash.ilike(search_pattern)
            | Transaction.sender_address.ilike(search_pattern)
            | Transaction.receiver_address.ilike(search_pattern)
        )
        count_query = count_query.where(
            Transaction.tx_hash.ilike(search_pattern)
            | Transaction.sender_address.ilike(search_pattern)
            | Transaction.receiver_address.ilike(search_pattern)
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(desc(Transaction.timestamp)).offset(offset).limit(page_size)
    result = await db.execute(query)
    txs = result.scalars().all()

    items = [
        {
            "id": tx.id,
            "tx_hash": tx.tx_hash,
            "sender_address": tx.sender_address,
            "receiver_address": tx.receiver_address,
            "blockchain": tx.blockchain,
            "amount": tx.amount,
            "amount_usd": tx.amount_usd,
            "gas_fee": tx.gas_fee,
            "token": tx.token,
            "block_number": tx.block_number,
            "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
            "status": tx.status,
            "is_flagged": tx.is_flagged,
        }
        for tx in txs
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }


@router.get("/export")
async def export_transactions(
    blockchain: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Transaction).order_by(desc(Transaction.timestamp)).limit(1000)
    if blockchain:
        query = query.where(Transaction.blockchain == blockchain)
    result = await db.execute(query)
    txs = result.scalars().all()

    items = [
        {
            "tx_hash": tx.tx_hash,
            "sender_address": tx.sender_address,
            "receiver_address": tx.receiver_address,
            "blockchain": tx.blockchain,
            "amount": tx.amount,
            "amount_usd": tx.amount_usd,
            "gas_fee": tx.gas_fee,
            "token": tx.token,
            "block_number": tx.block_number,
            "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
            "status": tx.status,
            "is_flagged": tx.is_flagged,
        }
        for tx in txs
    ]
    csv_bytes = generate_csv(items)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get("/{tx_hash}")
async def get_transaction(tx_hash: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Transaction).where(Transaction.tx_hash == tx_hash)
    )
    tx = result.scalar_one_or_none()
    if not tx:
        return {
            "tx_hash": tx_hash,
            "error": "Transaction not found in database. Sync the blockchain first.",
        }
    return {
        "id": tx.id,
        "tx_hash": tx.tx_hash,
        "sender_address": tx.sender_address,
        "receiver_address": tx.receiver_address,
        "blockchain": tx.blockchain,
        "amount": tx.amount,
        "amount_usd": tx.amount_usd,
        "gas_fee": tx.gas_fee,
        "token": tx.token,
        "block_number": tx.block_number,
        "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
        "status": tx.status,
        "is_flagged": tx.is_flagged,
    }


@router.post("/upload")
async def upload_transactions(file: UploadFile = File(...)):
    content = await file.read()
    rows = parse_csv(content)
    return {"imported": len(rows), "message": f"Successfully processed {len(rows)} transactions from CSV"}
