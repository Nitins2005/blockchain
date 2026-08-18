from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WalletResponse(BaseModel):
    id: int
    address: str
    blockchain: str
    label: Optional[str]
    tx_count: int
    balance: float
    first_seen: Optional[datetime]
    last_active: Optional[datetime]
    is_blacklisted: bool
    fraud_score: Optional[float]
    risk_level: Optional[str]
    category: Optional[str]

    class Config:
        from_attributes = True

class WalletCreate(BaseModel):
    address: str
    blockchain: str
    label: Optional[str] = None
