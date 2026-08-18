from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlockchainConfigUpdate(BaseModel):
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: Optional[bool] = None

class BlockchainConfigResponse(BaseModel):
    id: int
    blockchain: str
    display_name: str
    api_url: Optional[str]
    is_enabled: bool
    last_sync: Optional[datetime]
    tx_count: int
    wallet_count: int
    block_height: int
    sync_status: str

    class Config:
        from_attributes = True
