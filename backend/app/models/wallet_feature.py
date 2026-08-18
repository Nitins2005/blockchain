from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class WalletFeature(Base):
    __tablename__ = "wallet_features"
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), index=True, nullable=False)
    blockchain = Column(String(50))
    incoming_tx = Column(Integer, default=0)
    outgoing_tx = Column(Integer, default=0)
    avg_tx_amount = Column(Float, default=0.0)
    max_tx_amount = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    active_days = Column(Integer, default=0)
    gas_usage = Column(Float, default=0.0)
    token_diversity = Column(Integer, default=1)
    neighbor_count = Column(Integer, default=0)
    degree_centrality = Column(Float, default=0.0)
    betweenness_centrality = Column(Float, default=0.0)
    pagerank = Column(Float, default=0.0)
    clustering_coefficient = Column(Float, default=0.0)
    cross_chain_tx_count = Column(Integer, default=0)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
