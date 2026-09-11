from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.neo4j_client import neo4j_client
from app.blockchain.graph_builder import get_ego_graph_from_neo4j
from app.services.mock_data_service import generate_wallet_address, BLOCKCHAINS
import random
import hashlib
from datetime import datetime, timedelta

router = APIRouter()


def _generate_mock_ego_graph(center_address: str, n_neighbors: int = 15):
    """Fallback mock graph when Neo4j is not connected."""
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
            "color": colors.get(center_risk, "#6366f1"),
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
                "color": colors.get(risk, "#6366f1"),
            }
        })

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
async def get_graph_stats(db: AsyncSession = Depends(get_db)):
    wallet_count = await db.execute(select(func.count(Wallet.id)))
    tx_count = await db.execute(select(func.count(Transaction.id)))
    n = wallet_count.scalar() or 0
    e = tx_count.scalar() or 0
    density = (2 * e) / (n * (n - 1)) if n > 1 else 0

    if neo4j_client.is_connected:
        neo_stats = neo4j_client.get_graph_stats()
        return {
            "node_count": neo_stats.get("nodes", n),
            "edge_count": neo_stats.get("edges", e),
            "graph_density": neo_stats.get("density", round(density, 6)),
            "source": "neo4j",
        }

    return {
        "node_count": n,
        "edge_count": e,
        "graph_density": round(density, 6),
        "source": "postgresql",
    }


@router.get("/{address}")
async def get_graph(address: str, hops: int = 1):
    if neo4j_client.is_connected:
        graph = get_ego_graph_from_neo4j(address, hops=hops)
        if graph["nodes"]:
            return graph

    return _generate_mock_ego_graph(address, n_neighbors=15 * hops)
