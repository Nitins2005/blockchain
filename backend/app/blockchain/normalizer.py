import logging
from typing import List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import Transaction
from app.blockchain.base import NormalizedTransaction

logger = logging.getLogger(__name__)


async def store_transactions(
    db: AsyncSession, transactions: List[NormalizedTransaction]
) -> int:
    """Store normalized transactions in PostgreSQL. Returns count of newly stored."""
    stored = 0
    for tx in transactions:
        existing = await db.execute(
            select(Transaction).where(Transaction.tx_hash == tx.tx_hash)
        )
        if existing.scalar_one_or_none():
            continue

        db_tx = Transaction(
            tx_hash=tx.tx_hash,
            sender_address=tx.sender_address,
            receiver_address=tx.receiver_address,
            blockchain=tx.blockchain,
            amount=tx.amount,
            amount_usd=tx.amount_usd,
            gas_fee=tx.gas_fee,
            gas_fee_usd=tx.gas_fee_usd,
            token=tx.token,
            block_number=tx.block_number,
            timestamp=tx.timestamp,
            status=tx.status,
            is_flagged=tx.is_flagged,
        )
        db.add(db_tx)
        stored += 1

    if stored > 0:
        await db.commit()
    return stored


async def store_wallets(
    db: AsyncSession, transactions: List[NormalizedTransaction], blockchain: str
) -> int:
    """Ensure all wallet addresses from transactions exist in the wallets table."""
    from app.models.wallet import Wallet
    from sqlalchemy import func

    addresses = set()
    for tx in transactions:
        if tx.sender_address:
            addresses.add(tx.sender_address)
        if tx.receiver_address:
            addresses.add(tx.receiver_address)

    stored = 0
    for addr in addresses:
        existing = await db.execute(
            select(Wallet).where(Wallet.address == addr)
        )
        if existing.scalar_one_or_none():
            continue
        db_wallet = Wallet(
            address=addr,
            blockchain=blockchain,
            first_seen=tx.timestamp if tx else datetime.now(timezone.utc),
        )
        db.add(db_wallet)
        stored += 1

    if stored > 0:
        await db.commit()
    return stored
