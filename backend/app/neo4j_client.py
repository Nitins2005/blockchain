from neo4j import GraphDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self._driver = None
        self._connected = False

    def connect(self):
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            self._driver.verify_connectivity()
            self._connected = True
            logger.info("Neo4j connected successfully")
        except Exception as e:
            logger.warning(f"Neo4j connection failed (running in mock mode): {e}")
            self._connected = False

    def close(self):
        if self._driver:
            self._driver.close()

    @property
    def is_connected(self):
        return self._connected

    def run_query(self, query: str, parameters: dict = None):
        if not self._connected:
            return []
        with self._driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def create_wallet_node(self, address: str, blockchain: str, fraud_score: float = 0.0):
        if not self._connected:
            return None
        query = """
        MERGE (w:Wallet {address: $address})
        SET w.blockchain = $blockchain, w.fraud_score = $fraud_score
        RETURN w
        """
        return self.run_query(query, {"address": address, "blockchain": blockchain, "fraud_score": fraud_score})

    def create_transaction_edge(self, sender: str, receiver: str, tx_hash: str, amount: float, timestamp: str, blockchain: str):
        if not self._connected:
            return None
        query = """
        MERGE (s:Wallet {address: $sender})
        MERGE (r:Wallet {address: $receiver})
        CREATE (s)-[:SENT {tx_hash: $tx_hash, amount: $amount, timestamp: $timestamp, blockchain: $blockchain}]->(r)
        """
        return self.run_query(query, {"sender": sender, "receiver": receiver, "tx_hash": tx_hash, "amount": amount, "timestamp": timestamp, "blockchain": blockchain})

    def get_wallet_neighbors(self, address: str, hops: int = 2):
        if not self._connected:
            return {"nodes": [], "edges": []}
        query = """
        MATCH path = (w:Wallet {address: $address})-[:SENT*1..2]-(neighbor:Wallet)
        RETURN path LIMIT 100
        """
        return self.run_query(query, {"address": address})

    def get_graph_stats(self):
        if not self._connected:
            return {"nodes": 0, "edges": 0, "components": 0, "density": 0.0}
        node_count = self.run_query("MATCH (w:Wallet) RETURN count(w) as count")
        edge_count = self.run_query("MATCH ()-[r:SENT]->() RETURN count(r) as count")
        n = node_count[0]['count'] if node_count else 0
        e = edge_count[0]['count'] if edge_count else 0
        density = (2 * e) / (n * (n - 1)) if n > 1 else 0
        return {"nodes": n, "edges": e, "components": 1, "density": round(density, 6)}

neo4j_client = Neo4jClient()
