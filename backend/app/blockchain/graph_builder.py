import logging
from typing import List
from app.blockchain.base import NormalizedTransaction
from app.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)


def build_graph_from_transactions(transactions: List[NormalizedTransaction]) -> dict:
    """Store transactions as nodes and edges in Neo4j. Returns counts."""
    if not neo4j_client.is_connected:
        logger.warning("Neo4j not connected — skipping graph build")
        return {"wallets_created": 0, "edges_created": 0}

    wallets_created = 0
    edges_created = 0

    for tx in transactions:
        if tx.sender_address:
            neo4j_client.create_wallet_node(tx.sender_address, tx.blockchain)
            wallets_created += 1
        if tx.receiver_address:
            neo4j_client.create_wallet_node(tx.receiver_address, tx.blockchain)
            wallets_created += 1
        if tx.sender_address and tx.receiver_address:
            neo4j_client.create_transaction_edge(
                sender=tx.sender_address,
                receiver=tx.receiver_address,
                tx_hash=tx.tx_hash,
                amount=tx.amount,
                timestamp=tx.timestamp.isoformat() if tx.timestamp else "",
                blockchain=tx.blockchain,
            )
            edges_created += 1

    return {"wallets_created": wallets_created, "edges_created": edges_created}


def get_ego_graph_from_neo4j(address: str, hops: int = 1) -> dict:
    """Extract ego-graph centered on an address from Neo4j."""
    if not neo4j_client.is_connected:
        return {"nodes": [], "edges": []}

    query = """
    MATCH (center:Wallet {address: $address})-[r:SENT*1..""" + str(hops) + """]->(neighbor:Wallet)
    WITH center, r, neighbor
    RETURN DISTINCT neighbor.address AS addr, neighbor.blockchain AS chain,
           neighbor.fraud_score AS fraud_score
    LIMIT 50
    """
    neighbor_records = neo4j_client.run_query(query, {"address": address})

    edge_query = """
    MATCH (center:Wallet {address: $address})-[r:SENT]->(neighbor:Wallet)
    RETURN center.address AS source, neighbor.address AS target,
           r.tx_hash AS tx_hash, r.amount AS amount,
           r.timestamp AS timestamp, r.blockchain AS blockchain
    LIMIT 100
    """
    edge_records = neo4j_client.run_query(edge_query, {"address": address})

    reverse_query = """
    MATCH (neighbor:Wallet)-[r:SENT]->(center:Wallet {address: $address})
    RETURN neighbor.address AS source, center.address AS target,
           r.tx_hash AS tx_hash, r.amount AS amount,
           r.timestamp AS timestamp, r.blockchain AS blockchain
    LIMIT 100
    """
    reverse_records = neo4j_client.run_query(reverse_query, {"address": address})

    colors = {"low": "#10b981", "medium": "#f59e0b", "high": "#f97316", "critical": "#ef4444"}

    nodes = []
    nodes.append({
        "data": {
            "id": address,
            "label": address[:10] + "...",
            "address": address,
            "risk_level": "medium",
            "fraud_score": 0.5,
            "is_center": True,
            "blockchain": "ethereum",
            "tx_count": len(edge_records) + len(reverse_records),
            "color": "#6366f1",
        }
    })

    seen = {address}
    for rec in neighbor_records:
        addr = rec["addr"]
        if addr in seen:
            continue
        seen.add(addr)
        fraud = rec.get("fraud_score") or 0.0
        risk = "critical" if fraud >= 0.8 else "high" if fraud >= 0.6 else "medium" if fraud >= 0.3 else "low"
        nodes.append({
            "data": {
                "id": addr,
                "label": addr[:8] + "...",
                "address": addr,
                "risk_level": risk,
                "fraud_score": round(fraud, 3),
                "is_center": False,
                "blockchain": rec.get("chain") or "ethereum",
                "tx_count": 0,
                "color": colors.get(risk, "#6366f1"),
            }
        })

    edges = []
    all_edges = edge_records + reverse_records
    for rec in all_edges:
        edges.append({
            "data": {
                "id": rec["tx_hash"],
                "source": rec["source"],
                "target": rec["target"],
                "amount": round(float(rec["amount"]), 4) if rec["amount"] else 0,
                "tx_hash": rec["tx_hash"],
                "blockchain": rec.get("blockchain") or "ethereum",
                "timestamp": rec.get("timestamp") or "",
            }
        })

    return {"nodes": nodes, "edges": edges}
