from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), unique=True, index=True, nullable=False)
    blockchain = Column(String(50), nullable=False)
    label = Column(String(255))
    tx_count = Column(Integer, default=0)
    balance = Column(Float, default=0.0)
    first_seen = Column(DateTime(timezone=True))
    last_active = Column(DateTime(timezone=True))
    is_blacklisted = Column(Boolean, default=False)
    fraud_score = Column(Float)
    risk_level = Column(String(20))
    category = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
