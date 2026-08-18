from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlacklistCreate(BaseModel):
    address: str
    blockchain: str
    category: str  # scam, mixer, exchange, darknet
    reason: Optional[str] = None
    source: Optional[str] = None
    confidence: str = "high"

class BlacklistUpdate(BaseModel):
    reason: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class BlacklistResponse(BaseModel):
    id: int
    address: str
    blockchain: str
    category: str
    reason: Optional[str]
    source: Optional[str]
    confidence: str
    is_active: bool
    added_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
