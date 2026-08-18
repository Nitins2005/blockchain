from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(255), unique=True, index=True, nullable=False)
    sender_address = Column(String(255), index=True, nullable=False)
    receiver_address = Column(String(255), index=True, nullable=False)
    blockchain = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    amount_usd = Column(Float)
    gas_fee = Column(Float)
    gas_fee_usd = Column(Float)
    token = Column(String(50), default="NATIVE")
    block_number = Column(BigInteger)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="confirmed")
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
