from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), index=True, nullable=False)
    fraud_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(50), default="mock-v1.0")
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WalletCategory(Base):
    __tablename__ = "wallet_categories"
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), index=True, nullable=False)
    category = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(50), default="mock-v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
