from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class FraudPredictionResponse(BaseModel):
    wallet_address: str
    fraud_score: float
    risk_level: str
    confidence: float
    last_activity: Optional[datetime]
    tx_count: int
    connected_wallets: int
    cross_chain_activity: bool
    prediction_time: datetime
    model_version: str

class WalletAttributionResponse(BaseModel):
    wallet_address: str
    category: str
    confidence: float
    secondary_categories: List[dict]
    prediction_time: datetime
    model_version: str

class ExplanationResponse(BaseModel):
    wallet_address: str
    top_features: List[dict]
    neighbor_influence: List[dict]
    important_transactions: List[dict]
    temporal_activity: List[dict]
    risk_factors: List[str]
    reasoning_text: str
    fraud_score: float
