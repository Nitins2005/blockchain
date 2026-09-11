import logging
import math
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.models.wallet_feature import WalletFeature
from app.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

FEATURE_NAMES = [
    "incoming_tx", "outgoing_tx", "avg_tx_amount", "max_tx_amount",
    "balance", "active_days", "gas_usage", "token_diversity",
    "neighbor_count", "degree_centrality", "betweenness_centrality",
    "pagerank", "clustering_coefficient", "cross_chain_tx_count",
]


def _compute_basic_features(transactions: list) -> dict:
    """Compute basic transaction-level features from a list of Transaction ORM objects."""
    incoming = [t for t in transactions if t.receiver_address]
    outgoing = [t for t in transactions if t.sender_address]

    amounts = [float(t.amount) for t in transactions if t.amount]
    avg_amount = sum(amounts) / len(amounts) if amounts else 0.0
    max_amount = max(amounts) if amounts else 0.0

    gas_total = sum(float(t.gas_fee) for t in transactions if t.gas_fee)

    tokens = set(t.token for t in transactions if t.token)
    blockchains = set(t.blockchain for t in transactions if t.blockchain)
    cross_chain = sum(1 for t in transactions if len(blockchains) > 1)

    timestamps = [t.timestamp for t in transactions if t.timestamp]
    if timestamps:
        dates = set(ts.date() for ts in timestamps)
        active_days = len(dates)
        balance = sum(float(t.amount) for t in outgoing) - sum(float(t.amount) for t in incoming)
    else:
        active_days = 0
        balance = 0.0

    return {
        "incoming_tx": len(incoming),
        "outgoing_tx": len(outgoing),
        "avg_tx_amount": round(avg_amount, 6),
        "max_tx_amount": round(max_amount, 6),
        "balance": round(balance, 6),
        "active_days": active_days,
        "gas_usage": round(gas_total, 6),
        "token_diversity": len(tokens) if tokens else 1,
        "cross_chain_tx_count": cross_chain,
    }


def _compute_graph_features(address: str) -> dict:
    """Compute graph-derived features from Neo4j."""
    if not neo4j_client.is_connected:
        return {
            "neighbor_count": 0, "degree_centrality": 0.0,
            "betweenness_centrality": 0.0, "pagerank": 0.0,
            "clustering_coefficient": 0.0,
        }

    degree = neo4j_client.get_node_degree(address)
    pagerank_data = neo4j_client.get_wallet_features_from_graph(address)

    total = degree["total_degree"]
    in_d = degree["in_degree"]
    out_d = degree["out_degree"]

    in_ratio = in_d / total if total > 0 else 0.0
    out_ratio = out_d / total if total > 0 else 0.0
    degree_centrality = min(total / 1000.0, 1.0)

    clustering = _estimate_clustering_coefficient(address)

    return {
        "neighbor_count": total,
        "degree_centrality": round(degree_centrality, 6),
        "betweenness_centrality": round(in_ratio * out_ratio * 2, 6),
        "pagerank": round(float(pagerank_data.get("pagerank", 0.0)), 6),
        "clustering_coefficient": round(clustering, 6),
    }


def _estimate_clustering_coefficient(address: str) -> float:
    """Estimate local clustering coefficient via neighbor overlap query."""
    query = """
    MATCH (w:Wallet {address: $address})-[:SENT]->(neighbor:Wallet)
    WITH w, collect(DISTINCT neighbor.address) AS neighbors
    UNWIND neighbors AS n1
    UNWIND neighbors AS n2
    WITH w, n1, n2 WHERE n1 < n2
    OPTIONAL MATCH (a:Wallet {address: n1})-[:SENT]->(b:Wallet {address: n2})
    WITH w, count(DISTINCT a) AS triangles, size(
        CASE WHEN n1 < n2 THEN [1] ELSE [] END
    ) AS possible
    RETURN
        CASE WHEN size(neighbors) < 2 THEN 0.0
             ELSE toFloat(count(DISTINCT CASE WHEN a IS NOT NULL THEN n1 END)) /
                  (size(neighbors) * (size(neighbors) - 1) / 2.0)
        END AS clustering_coeff
    LIMIT 1
    """
    result = neo4j_client.run_query(query, {"address": address})
    if result and result[0].get("clustering_coeff") is not None:
        return float(result[0]["clustering_coeff"])
    return 0.0


async def compute_wallet_features(
    db: AsyncSession,
    address: str,
    blockchain: str = "ethereum",
    include_graph: bool = True,
) -> WalletFeature:
    """Compute and store all features for a single wallet."""
    result = await db.execute(
        select(Transaction).where(
            (Transaction.sender_address == address.lower())
            | (Transaction.receiver_address == address.lower())
        ).order_by(Transaction.timestamp)
    )
    transactions = list(result.scalars().all())

    features = _compute_basic_features(transactions)

    if include_graph and neo4j_client.is_connected:
        graph_features = _compute_graph_features(address.lower())
        features.update(graph_features)
    else:
        features.update({
            "neighbor_count": 0, "degree_centrality": 0.0,
            "betweenness_centrality": 0.0, "pagerank": 0.0,
            "clustering_coefficient": 0.0,
        })

    existing = await db.execute(
        select(WalletFeature).where(
            WalletFeature.wallet_address == address.lower()
        )
    )
    wf = existing.scalar_one_or_none()

    if wf:
        for k, v in features.items():
            setattr(wf, k, v)
        wf.computed_at = datetime.now(timezone.utc)
    else:
        wf = WalletFeature(
            wallet_address=address.lower(),
            blockchain=blockchain,
            **features,
        )
        db.add(wf)

    await db.commit()
    await db.refresh(wf)
    return wf


async def compute_all_features(
    db: AsyncSession,
    blockchain: Optional[str] = None,
    include_graph: bool = True,
) -> int:
    """Compute features for all wallets with transactions. Returns count."""
    query = select(Transaction.sender_address).distinct()
    if blockchain:
        query = query.where(Transaction.blockchain == blockchain)
    sender_result = await db.execute(query)
    senders = set(r[0] for r in sender_result.all())

    query = select(Transaction.receiver_address).distinct()
    if blockchain:
        query = query.where(Transaction.blockchain == blockchain)
    receiver_result = await db.execute(query)
    receivers = set(r[0] for r in receiver_result.all())

    all_addresses = senders | receivers
    count = 0
    for addr in all_addresses:
        if addr:
            await compute_wallet_features(db, addr, blockchain or "ethereum", include_graph)
            count += 1

    return count


def get_feature_vector(wf: WalletFeature) -> dict:
    """Convert a WalletFeature ORM object into a numeric feature vector."""
    values = [
        float(wf.incoming_tx), float(wf.outgoing_tx),
        wf.avg_tx_amount, wf.max_tx_amount,
        wf.balance, float(wf.active_days),
        wf.gas_usage, float(wf.token_diversity),
        float(wf.neighbor_count), wf.degree_centrality,
        wf.betweenness_centrality, wf.pagerank,
        wf.clustering_coefficient, float(wf.cross_chain_tx_count),
    ]
    return {
        "wallet_address": wf.wallet_address,
        "blockchain": wf.blockchain,
        "feature_names": FEATURE_NAMES,
        "feature_values": values,
    }


def get_gnn_subgraph_data(center: str, hops: int = 2) -> dict:
    """Extract a subgraph from Neo4j suitable for GNN input."""
    if not neo4j_client.is_connected:
        return {"nodes": [], "edges": [], "node_features": {}}

    subgraph = neo4j_client.get_subgraph_for_gnn(center, hops=hops, max_nodes=500)

    node_features = {}
    for node in subgraph["nodes"]:
        addr = node["address"]
        features = neo4j_client.get_wallet_features_from_graph(addr)
        node_features[addr] = {
            "fraud_score": node.get("fraud_score", 0.0),
            "pagerank": features.get("pagerank", 0.0),
            "in_degree": features.get("in_degree", 0),
            "out_degree": features.get("out_degree", 0),
            "blockchain_id": _blockchain_to_id(node.get("blockchain", "ethereum")),
        }

    center_features = neo4j_client.get_wallet_features_from_graph(center)
    node_features[center] = {
        "fraud_score": 0.0,
        "pagerank": center_features.get("pagerank", 0.0),
        "in_degree": center_features.get("in_degree", 0),
        "out_degree": center_features.get("out_degree", 0),
        "blockchain_id": _blockchain_to_id("ethereum"),
    }

    return {
        "nodes": subgraph["nodes"],
        "edges": subgraph["edges"],
        "node_features": node_features,
    }


BLOCKCHAIN_IDS = {"bitcoin": 0, "ethereum": 1, "bnb": 2, "polygon": 3, "tron": 4}


def _blockchain_to_id(chain: str) -> int:
    return BLOCKCHAIN_IDS.get(chain, 1)
