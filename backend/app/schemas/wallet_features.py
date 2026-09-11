from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WalletFeatureCreate(BaseModel):
    wallet_address: str
    blockchain: str = "ethereum"
    incoming_tx: int = 0
    outgoing_tx: int = 0
    avg_tx_amount: float = 0.0
    max_tx_amount: float = 0.0
    balance: float = 0.0
    active_days: int = 0
    gas_usage: float = 0.0
    token_diversity: int = 1
    neighbor_count: int = 0
    degree_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    pagerank: float = 0.0
    clustering_coefficient: float = 0.0
    cross_chain_tx_count: int = 0


class WalletFeatureResponse(BaseModel):
    id: int
    wallet_address: str
    blockchain: str
    incoming_tx: int
    outgoing_tx: int
    avg_tx_amount: float
    max_tx_amount: float
    balance: float
    active_days: int
    gas_usage: float
    token_diversity: int
    neighbor_count: int
    degree_centrality: float
    betweenness_centrality: float
    pagerank: float
    clustering_coefficient: float
    cross_chain_tx_count: int
    computed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FeatureComputeRequest(BaseModel):
    wallet_address: str
    blockchain: str = "ethereum"
    include_graph_metrics: bool = True


class FeatureComputeBatchRequest(BaseModel):
    addresses: list[str]
    blockchain: str = "ethereum"
    include_graph_metrics: bool = True


class FeatureVector(BaseModel):
    wallet_address: str
    blockchain: str
    feature_names: list[str]
    feature_values: list[float]
    raw_features: Optional[WalletFeatureResponse] = None
