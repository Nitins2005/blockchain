from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class InvestigationStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"
    archived = "archived"

class Investigation(Base):
    __tablename__ = "investigations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(InvestigationStatus), default=InvestigationStatus.open)
    priority = Column(String(20), default="medium")
    created_by_id = Column(Integer, index=True)
    assigned_to_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class InvestigationWallet(Base):
    __tablename__ = "investigation_wallets"
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), index=True)
    wallet_address = Column(String(255), nullable=False)
    blockchain = Column(String(50))
    added_at = Column(DateTime(timezone=True), server_default=func.now())

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
