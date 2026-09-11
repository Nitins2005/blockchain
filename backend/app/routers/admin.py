from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.prediction import Prediction
from app.models.investigation import Investigation
from app.neo4j_client import neo4j_client
from app.services.model_service import state as model_state
import psutil
import time

router = APIRouter()

_start_time = time.time()


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    wallet_count = await db.execute(select(func.count(Wallet.id)))
    tx_count = await db.execute(select(func.count(Transaction.id)))
    total_wallets = wallet_count.scalar() or 0
    total_transactions = tx_count.scalar() or 0

    blacklisted = await db.execute(
        select(func.count(Wallet.id)).where(Wallet.is_blacklisted == True)
    )
    blacklisted_count = blacklisted.scalar() or 0

    high_risk = await db.execute(
        select(func.count(Wallet.id)).where(Wallet.fraud_score >= 0.7)
    )
    high_risk_count = high_risk.scalar() or 0

    avg_score = await db.execute(select(func.avg(Wallet.fraud_score)))
    avg_fraud = avg_score.scalar()

    chain_dist = await db.execute(
        select(Wallet.blockchain, func.count(Wallet.id)).group_by(Wallet.blockchain)
    )
    blockchain_distribution = {row[0]: row[1] for row in chain_dist.all()}

    recent_tx = await db.execute(
        select(Transaction.timestamp).order_by(desc(Transaction.timestamp)).limit(1)
    )
    last_tx = recent_tx.scalar()

    return {
        "total_wallets": total_wallets,
        "total_transactions": total_transactions,
        "fraudulent_wallets": high_risk_count,
        "blacklisted_wallets": blacklisted_count,
        "avg_fraud_score": round(float(avg_fraud) if avg_fraud else 0.0, 4),
        "blockchain_distribution": blockchain_distribution,
        "last_activity": last_tx.isoformat() if last_tx else None,
        "neo4j_connected": neo4j_client.is_connected,
        "model_status": "ready" if model_state.fraud_model else "untrained",
    }


@router.get("/fraud-trend")
async def get_fraud_trend(db: AsyncSession = Depends(get_db)):
    base = datetime.now(timezone.utc)
    result = []
    for i in range(30):
        day = (base - timedelta(days=29 - i)).date()
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        total_q = await db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.timestamp >= day_start,
                Transaction.timestamp < day_end,
            )
        )
        total = total_q.scalar() or 0

        flagged_q = await db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.timestamp >= day_start,
                Transaction.timestamp < day_end,
                Transaction.is_flagged == True,
            )
        )
        flagged = flagged_q.scalar() or 0

        result.append({
            "date": day.isoformat(),
            "flagged": flagged,
            "total": total,
            "score_avg": round(flagged / total, 3) if total > 0 else 0.0,
        })
    return result


@router.get("/volume-trend")
async def get_volume_trend(db: AsyncSession = Depends(get_db)):
    base = datetime.now(timezone.utc)
    chains = ["ethereum", "bnb", "bitcoin", "polygon", "tron"]
    result = []
    for i in range(14):
        day = (base - timedelta(days=13 - i)).date()
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        entry = {"date": day.isoformat()}
        for chain in chains:
            q = await db.execute(
                select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                    Transaction.blockchain == chain,
                    Transaction.timestamp >= day_start,
                    Transaction.timestamp < day_end,
                )
            )
            entry[chain] = round(float(q.scalar() or 0), 2)
        result.append(entry)
    return result


@router.get("/blockchain-distribution")
async def get_blockchain_distribution(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Wallet.blockchain, func.count(Wallet.id)).group_by(Wallet.blockchain)
    )
    rows = result.all()
    chain_names = {"ethereum": "Ethereum", "bitcoin": "Bitcoin", "bnb": "BNB Chain",
                   "polygon": "Polygon", "tron": "Tron"}
    return [{"name": chain_names.get(r[0], r[0].title()), "value": r[1]} for r in rows]


@router.get("/category-distribution")
async def get_category_distribution(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Wallet.category, func.count(Wallet.id))
        .where(Wallet.category.isnot(None))
        .group_by(Wallet.category)
    )
    rows = result.all()
    return [{"name": r[0] or "Unknown", "value": r[1]} for r in rows]


@router.get("/recent-investigations")
async def get_recent_investigations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Investigation).order_by(desc(Investigation.created_at)).limit(10)
    )
    invs = result.scalars().all()
    return [
        {
            "id": inv.id,
            "title": inv.title,
            "status": inv.status,
            "priority": inv.priority,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "wallet_count": 0,
        }
        for inv in invs
    ]


@router.get("/system-health")
async def get_system_health():
    neo4j_ok = neo4j_client.is_connected
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.1)

    return {
        "api_status": "operational",
        "database_status": "connected",
        "neo4j_status": "connected" if neo4j_ok else "disconnected",
        "model_status": "ready" if model_state.fraud_model else "untrained",
        "uptime_seconds": int(time.time() - _start_time),
        "memory_usage_mb": round(mem.used / (1024 * 1024), 1),
        "memory_usage_percent": mem.percent,
        "cpu_usage_percent": round(cpu, 1),
    }
