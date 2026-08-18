from fastapi import APIRouter
from typing import Optional
import random
from datetime import datetime
from app.services.mock_data_service import BLOCKCHAINS

router = APIRouter()

def _generate_features(address: str, blockchain: str = None):
    seed = sum(ord(c) for c in address)
    random.seed(seed)
    features = {
        "wallet_address": address,
        "blockchain": blockchain or random.choice(BLOCKCHAINS),
        "incoming_tx": random.randint(5, 5000),
        "outgoing_tx": random.randint(5, 5000),
        "avg_tx_amount": round(random.uniform(0.001, 100), 6),
        "max_tx_amount": round(random.uniform(10, 10000), 4),
        "balance": round(random.uniform(0, 1000), 6),
        "active_days": random.randint(1, 1825),
        "gas_usage": round(random.uniform(0.001, 10), 6),
        "token_diversity": random.randint(1, 20),
        "neighbor_count": random.randint(2, 500),
        "degree_centrality": round(random.uniform(0.0001, 0.9), 6),
        "betweenness_centrality": round(random.uniform(0, 0.5), 6),
        "pagerank": round(random.uniform(0, 0.01), 8),
        "clustering_coefficient": round(random.uniform(0, 1), 6),
        "cross_chain_tx_count": random.randint(0, 50),
        "computed_at": datetime.utcnow().isoformat()
    }
    random.seed()
    return features

@router.get("/wallet/{address}")
async def get_wallet_features(address: str, blockchain: Optional[str] = None):
    return _generate_features(address, blockchain)

@router.post("/compute/{address}")
async def compute_features(address: str, blockchain: Optional[str] = None):
    features = _generate_features(address, blockchain)
    return {"message": "Features computed successfully", "features": features}

@router.post("/compute-all")
async def compute_all_features():
    return {"message": "Batch feature computation started",
            "job_id": f"feat-{random.randint(1000, 9999)}",
            "estimated_minutes": random.randint(5, 30)}
