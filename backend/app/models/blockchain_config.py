from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.sql import func
from app.database import Base

class BlockchainConfig(Base):
    __tablename__ = "blockchain_configs"
    id = Column(Integer, primary_key=True, index=True)
    blockchain = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100))
    api_url = Column(String(500))
    api_key_encrypted = Column(String(500))
    is_enabled = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True))
    tx_count = Column(BigInteger, default=0)
    wallet_count = Column(Integer, default=0)
    block_height = Column(BigInteger, default=0)
    sync_status = Column(String(50), default="idle")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
