from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionResponse(BaseModel):
    id: int
    tx_hash: str
    sender_address: str
    receiver_address: str
    blockchain: str
    amount: float
    amount_usd: Optional[float]
    gas_fee: Optional[float]
    token: str
    block_number: Optional[int]
    timestamp: datetime
    status: str
    is_flagged: bool

    class Config:
        from_attributes = True

class TransactionFilter(BaseModel):
    blockchain: Optional[str] = None
    status: Optional[str] = None
    token: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20
