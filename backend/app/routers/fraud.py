from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import random
from datetime import datetime, timedelta
from app.services.mock_data_service import (
    get_fraud_prediction, generate_mock_wallets, generate_wallet_address
)

router = APIRouter()

class FraudPredictRequest(BaseModel):
    wallet_address: str
    blockchain: Optional[str] = None

@router.post("/predict")
async def predict_fraud(req: FraudPredictRequest):
    return get_fraud_prediction(req.wallet_address)

@router.get("/history/{address}")
async def get_prediction_history(address: str):
    history = []
    for i in range(random.randint(3, 10)):
        pred = get_fraud_prediction(address + str(i))
        pred["wallet_address"] = address
        pred["prediction_time"] = (datetime.utcnow() - timedelta(days=i*7)).isoformat()
        history.append(pred)
    return {"address": address, "history": history}

@router.get("/high-risk")
async def get_high_risk_wallets(page: int = 1, page_size: int = 20, blockchain: Optional[str] = None):
    wallets = generate_mock_wallets(50)
    high_risk = [w for w in wallets if w["fraud_score"] > 0.6]
    if blockchain:
        high_risk = [w for w in high_risk if w["blockchain"] == blockchain]
    start = (page - 1) * page_size
    return {
        "items": high_risk[start:start + page_size],
        "total": len(high_risk),
        "page": page,
        "page_size": page_size
    }

@router.get("/stats")
async def get_fraud_stats():
    return {
        "total_analyzed": random.randint(40000, 100000),
        "high_risk_count": random.randint(1000, 5000),
        "critical_count": random.randint(100, 500),
        "avg_fraud_score": round(random.uniform(0.2, 0.45), 3),
        "detection_rate": round(random.uniform(0.88, 0.97), 3),
        "false_positive_rate": round(random.uniform(0.02, 0.08), 3)
    }
