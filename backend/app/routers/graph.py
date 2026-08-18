from fastapi import APIRouter
from typing import Optional
import random
import hashlib
from datetime import datetime, timedelta
from app.services.mock_data_service import generate_wallet_address, BLOCKCHAINS
from app.neo4j_client import neo4j_client

router = APIRouter()

def _generate_ego_graph(center_address: str, n_neighbors: int = 15):
    """Generate a realistic mock transaction graph centered on an address."""
    random.seed(sum(ord(c) for c in center_address))
    risk_levels = ["low", "low", "medium", "medium", "high", "critical"]
    colors = {"low": "#10b981", "medium": "#f59e0b", "high": "#f97316", "critical": "#ef4444"}

    nodes = []
    edges = []

    center_risk = random.choice(risk_levels)
    nodes.append({
        "data": {
            "id": center_address,
            "label": center_address[:10] + "...",
            "address": center_address,
            "risk_level": center_risk,
            "fraud_score": round(random.uniform(0.5, 0.99), 3),
            "is_center": True,
            "blockchain": random.choice(BLOCKCHAINS),
            "tx_count": random.randint(50, 5000),
            "color": colors.get(center_risk, "#6366f1")
        }
    })

    neighbor_addresses = [generate_wallet_address(random.choice(BLOCKCHAINS)) for _ in range(n_neighbors)]

    for addr in neighbor_addresses:
        risk = random.choice(risk_levels)
        nodes.append({
            "data": {
                "id": addr,
                "label": addr[:8] + "...",
                "address": addr,
                "risk_level": risk,
                "fraud_score": round(random.uniform(0.05, 0.95), 3),
                "is_center": False,
                "blockchain": random.choice(BLOCKCHAINS),
                "tx_count": random.randint(1, 1000),
                "color": colors.get(risk, "#6366f1")
            }
        })

    # Edges from center to neighbors
    for addr in neighbor_addresses:
        tx_hash = f"0x{hashlib.sha256(f'{center_address}{addr}'.encode()).hexdigest()[:40]}"
        if random.random() > 0.5:
            edges.append({"data": {"id": tx_hash, "source": center_address, "target": addr,
                                    "amount": round(random.uniform(0.01, 100), 4),
                                    "tx_hash": tx_hash, "blockchain": random.choice(BLOCKCHAINS),
                                    "timestamp": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat()}})
        else:
            edges.append({"data": {"id": tx_hash, "source": addr, "target": center_address,
                                    "amount": round(random.uniform(0.01, 100), 4),
                                    "tx_hash": tx_hash, "blockchain": random.choice(BLOCKCHAINS),
                                    "timestamp": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat()}})

    # Some inter-neighbor edges
    for i in range(min(5, len(neighbor_addresses) - 1)):
        src = neighbor_addresses[i]
        tgt = neighbor_addresses[i + 1]
        tx_hash = f"0x{hashlib.sha256(f'{src}{tgt}'.encode()).hexdigest()[:40]}"
        edges.append({"data": {"id": tx_hash, "source": src, "target": tgt,
                                "amount": round(random.uniform(0.001, 50), 4),
                                "tx_hash": tx_hash, "blockchain": random.choice(BLOCKCHAINS),
                                "timestamp": (datetime.utcnow() - timedelta(days=random.randint(0, 180))).isoformat()}})

    random.seed()
    return {"nodes": nodes, "edges": edges}

@router.get("/stats")
async def get_graph_stats():
    return {
        "node_count": random.randint(1000000, 5000000),
        "edge_count": random.randint(5000000, 20000000),
        "graph_density": round(random.uniform(0.001, 0.01), 6)
    }

@router.get("/{address}")
async def get_graph(address: str, hops: int = 1):
    return _generate_ego_graph(address, n_neighbors=15 * hops)
