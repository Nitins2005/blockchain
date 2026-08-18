from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.mock_data_service import get_wallet_explanation

router = APIRouter()

class ExplainRequest(BaseModel):
    wallet_address: str
    blockchain: Optional[str] = None

@router.post("/explain")
async def explain_wallet(req: ExplainRequest):
    return get_wallet_explanation(req.wallet_address)

@router.get("/report/{address}")
async def get_explanation_report(address: str):
    return get_wallet_explanation(address)
