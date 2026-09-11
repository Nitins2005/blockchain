from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.services.graph_service import compute_wallet_features, get_feature_vector
from app.services.model_service import predict_fraud

router = APIRouter()


class FraudPredictRequest(BaseModel):
    wallet_address: str
    blockchain: Optional[str] = "ethereum"


@router.post("/predict")
async def predict_fraud_endpoint(req: FraudPredictRequest, db: AsyncSession = Depends(get_db)):
    wf = await compute_wallet_features(db, req.wallet_address, req.blockchain or "ethereum")
    fv = get_feature_vector(wf)
    pred = predict_fraud(fv["feature_values"])

    wallet_result = await db.execute(
        select(Wallet).where(Wallet.address == req.wallet_address.lower())
    )
    wallet = wallet_result.scalar_one_or_none()
    if wallet:
        wallet.fraud_score = pred["fraud_score"]
        wallet.risk_level = pred["risk_level"]
        db.add(wallet)
        await db.commit()

    pred["wallet_address"] = req.wallet_address
    pred["tx_count"] = wf.incoming_tx + wf.outgoing_tx
    pred["connected_wallets"] = wf.neighbor_count
    return pred


@router.get("/history/{address}")
async def get_prediction_history(address: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Wallet).where(Wallet.address == address.lower())
    )
    wallet = result.scalar_one_or_none()

    fraud_score = wallet.fraud_score if wallet and wallet.fraud_score else 0.5
    risk_level = wallet.risk_level if wallet and wallet.risk_level else "medium"

    return {
        "address": address,
        "history": [
            {
                "wallet_address": address,
                "fraud_score": fraud_score,
                "risk_level": risk_level,
                "prediction_time": datetime.now(timezone.utc).isoformat(),
                "model_version": "v1.0.0",
            }
        ],
    }


@router.get("/high-risk")
async def get_high_risk_wallets(
    page: int = 1, page_size: int = 20,
    blockchain: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Wallet).where(Wallet.fraud_score.isnot(None), Wallet.fraud_score >= 0.6)
    count_query = select(func.count(Wallet.id)).where(Wallet.fraud_score.isnot(None), Wallet.fraud_score >= 0.6)

    if blockchain:
        query = query.where(Wallet.blockchain == blockchain)
        count_query = count_query.where(Wallet.blockchain == blockchain)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(desc(Wallet.fraud_score)).offset(offset).limit(page_size)
    result = await db.execute(query)
    wallets = result.scalars().all()

    items = [
        {
            "address": w.address,
            "blockchain": w.blockchain,
            "fraud_score": w.fraud_score,
            "risk_level": w.risk_level or "unknown",
            "tx_count": w.tx_count or 0,
            "balance": w.balance or 0.0,
            "last_active": w.last_active.isoformat() if w.last_active else None,
        }
        for w in wallets
    ]

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/stats")
async def get_fraud_stats(db: AsyncSession = Depends(get_db)):
    total_q = await db.execute(select(func.count(Wallet.id)))
    total = total_q.scalar() or 0

    high_risk_q = await db.execute(
        select(func.count(Wallet.id)).where(Wallet.fraud_score.isnot(None), Wallet.fraud_score >= 0.7)
    )
    high_risk = high_risk_q.scalar() or 0

    critical_q = await db.execute(
        select(func.count(Wallet.id)).where(Wallet.fraud_score.isnot(None), Wallet.fraud_score >= 0.9)
    )
    critical = critical_q.scalar() or 0

    avg_q = await db.execute(
        select(func.avg(Wallet.fraud_score)).where(Wallet.fraud_score.isnot(None))
    )
    avg_score = avg_q.scalar()

    blacklisted_q = await db.execute(
        select(func.count(Wallet.id)).where(Wallet.is_blacklisted == True)
    )
    blacklisted = blacklisted_q.scalar() or 0

    return {
        "total_analyzed": total,
        "high_risk_count": high_risk,
        "critical_count": critical,
        "avg_fraud_score": round(float(avg_score) if avg_score else 0.0, 4),
        "blacklisted_count": blacklisted,
        "detection_rate": round(high_risk / total, 4) if total > 0 else 0.0,
    }
