from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta
from app.services.mock_data_service import get_wallet_attribution, WALLET_CATEGORIES

router = APIRouter()

class AttributionRequest(BaseModel):
    wallet_address: str
    blockchain: Optional[str] = None

@router.post("/predict")
async def predict_attribution(req: AttributionRequest):
    return get_wallet_attribution(req.wallet_address)

@router.get("/history/{address}")
async def get_attribution_history(address: str):
    history = []
    for i in range(random.randint(2, 6)):
        attr = get_wallet_attribution(address + str(i))
        attr["wallet_address"] = address
        attr["prediction_time"] = (datetime.utcnow() - timedelta(days=i*14)).isoformat()
        history.append(attr)
    return {"address": address, "history": history}

@router.get("/distribution")
async def get_distribution():
    return [{"category": cat, "count": random.randint(50, 2000)} for cat in WALLET_CATEGORIES]
