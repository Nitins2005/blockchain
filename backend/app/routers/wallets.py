from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.wallet import Wallet
from app.models.transaction import Transaction

router = APIRouter()


class WalletCreate(BaseModel):
    address: str
    blockchain: str
    label: Optional[str] = None


@router.get("")
async def list_wallets(
    page: int = 1, page_size: int = 20,
    blockchain: Optional[str] = None, risk_level: Optional[str] = None,
    search: Optional[str] = None, is_blacklisted: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Wallet)
    count_query = select(func.count(Wallet.id))

    if blockchain:
        query = query.where(Wallet.blockchain == blockchain)
        count_query = count_query.where(Wallet.blockchain == blockchain)
    if risk_level:
        query = query.where(Wallet.risk_level == risk_level)
        count_query = count_query.where(Wallet.risk_level == risk_level)
    if is_blacklisted is not None:
        query = query.where(Wallet.is_blacklisted == is_blacklisted)
        count_query = count_query.where(Wallet.is_blacklisted == is_blacklisted)
    if search:
        pattern = f"%{search}%"
        query = query.where(Wallet.address.ilike(pattern))
        count_query = count_query.where(Wallet.address.ilike(pattern))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(desc(Wallet.last_active)).offset(offset).limit(page_size)
    result = await db.execute(query)
    wallets = result.scalars().all()

    items = [
        {
            "id": w.id,
            "address": w.address,
            "blockchain": w.blockchain,
            "label": w.label,
            "tx_count": w.tx_count or 0,
            "balance": w.balance or 0.0,
            "fraud_score": w.fraud_score,
            "risk_level": w.risk_level,
            "category": w.category,
            "is_blacklisted": w.is_blacklisted,
            "first_seen": w.first_seen.isoformat() if w.first_seen else None,
            "last_active": w.last_active.isoformat() if w.last_active else None,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in wallets
    ]

    return {"items": items, "total": total, "page": page, "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if total > 0 else 0}


@router.get("/{address}")
async def get_wallet(address: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Wallet).where(Wallet.address == address.lower())
    )
    w = result.scalar_one_or_none()
    if not w:
        return {
            "address": address,
            "error": "Wallet not found. Sync the blockchain to populate wallet data.",
            "tx_count": 0,
            "balance": 0.0,
            "fraud_score": None,
            "risk_level": None,
            "is_blacklisted": False,
        }
    return {
        "id": w.id,
        "address": w.address,
        "blockchain": w.blockchain,
        "label": w.label,
        "tx_count": w.tx_count or 0,
        "balance": w.balance or 0.0,
        "fraud_score": w.fraud_score,
        "risk_level": w.risk_level,
        "category": w.category,
        "is_blacklisted": w.is_blacklisted,
        "first_seen": w.first_seen.isoformat() if w.first_seen else None,
        "last_active": w.last_active.isoformat() if w.last_active else None,
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }


@router.get("/{address}/transactions")
async def get_wallet_transactions(address: str, page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db)):
    query = select(Transaction).where(
        (Transaction.sender_address == address.lower())
        | (Transaction.receiver_address == address.lower())
    )
    count_q = select(func.count(Transaction.id)).where(
        (Transaction.sender_address == address.lower())
        | (Transaction.receiver_address == address.lower())
    )

    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(desc(Transaction.timestamp)).offset(offset).limit(page_size)
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

    return {"items": items, "total": total, "page": page, "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if total > 0 else 0}


@router.post("")
async def create_wallet(data: WalletCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Wallet).where(Wallet.address == data.address.lower())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Wallet already exists")

    wallet = Wallet(
        address=data.address.lower(),
        blockchain=data.blockchain,
        label=data.label,
    )
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return {
        "id": wallet.id,
        "address": wallet.address,
        "blockchain": wallet.blockchain,
        "label": wallet.label,
        "tx_count": 0,
        "balance": 0.0,
        "is_blacklisted": False,
    }


@router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    await db.delete(wallet)
    await db.commit()
    return {"message": "Wallet deleted"}
