from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), index=True, nullable=False)
    blockchain = Column(String(50))
    category = Column(String(100))  # scam, mixer, exchange, darknet
    reason = Column(Text)
    source = Column(String(255))
    confidence = Column(String(20), default="high")
    is_active = Column(Boolean, default=True)
    added_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
