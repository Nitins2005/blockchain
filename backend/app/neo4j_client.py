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

    def batch_create_wallet_nodes(self, wallets: list[dict]):
        if not self._connected or not wallets:
            return 0
        query = """
        UNWIND $wallets AS w
        MERGE (node:Wallet {address: w.address})
        SET node.blockchain = w.blockchain, node.fraud_score = COALESCE(w.fraud_score, 0.0)
        """
        self.run_query(query, {"wallets": wallets})
        return len(wallets)

    def batch_create_transaction_edges(self, edges: list[dict]):
        if not self._connected or not edges:
            return 0
        query = """
        UNWIND $edges AS e
        MERGE (s:Wallet {address: e.sender})
        MERGE (r:Wallet {address: e.receiver})
        CREATE (s)-[:SENT {
            tx_hash: e.tx_hash,
            amount: e.amount,
            timestamp: e.timestamp,
            blockchain: e.blockchain
        }]->(r)
        """
        self.run_query(query, {"edges": edges})
        return len(edges)

    def get_node_degree(self, address: str) -> dict:
        if not self._connected:
            return {"in_degree": 0, "out_degree": 0, "total_degree": 0}
        query = """
        MATCH (w:Wallet {address: $address})
        OPTIONAL MATCH (w)-[out:SENT]->()
        OPTIONAL MATCH ()-[inp:SENT]->(w)
        RETURN count(DISTINCT out) AS out_degree, count(DISTINCT inp) AS in_degree
        """
        result = self.run_query(query, {"address": address})
        if result:
            r = result[0]
            return {"in_degree": r["in_degree"], "out_degree": r["out_degree"],
                    "total_degree": r["in_degree"] + r["out_degree"]}
        return {"in_degree": 0, "out_degree": 0, "total_degree": 0}

    def compute_pagerank(self, iterations: int = 20, damping: float = 0.85) -> list[dict]:
        if not self._connected:
            return []
        n_result = self.run_query("MATCH (w:Wallet) RETURN count(w) AS n")
        n = n_result[0]["n"] if n_result else 0
        if n == 0:
            return []

        self.run_query("MATCH (w:Wallet) SET w.pagerank = 1.0 / $n", {"n": n})

        for _ in range(iterations):
            self.run_query("""
                MATCH (w:Wallet)
                WHERE exists((w)-[:SENT]->())
                OPTIONAL MATCH (w)-[:SENT]->(neighbor:Wallet)
                WITH w, COALESCE(sum(neighbor.pagerank), 0) AS rank_sum,
                     count(neighbor) AS out_count
                WHERE out_count > 0
                SET w.pagerank_new = (1 - $d) / $n + $d * rank_sum / out_count
            """, {"d": damping, "n": n})
            self.run_query("""
                MATCH (w:Wallet) WHERE w.pagerank_new IS NOT NULL
                SET w.pagerank = w.pagerank_new REMOVE w.pagerank_new
            """)

        result = self.run_query("MATCH (w:Wallet) RETURN w.address AS address, w.pagerank AS pagerank ORDER BY pagerank DESC LIMIT 50")
        return result

    def compute_node_similarities(self, max_pairs: int = 100) -> list[dict]:
        if not self._connected:
            return []
        query = """
        MATCH (a:Wallet)-[:SENT]->(common:Wallet)<-[:SENT]-(b:Wallet)
        WHERE a.address < b.address
        WITH a, b, count(common) AS shared_neighbors
        ORDER BY shared_neighbors DESC
        LIMIT $limit
        RETURN a.address AS node1, b.address AS node2, shared_neighbors
        """
        return self.run_query(query, {"limit": max_pairs})

    def get_wallet_features_from_graph(self, address: str) -> dict:
        if not self._connected:
            return {}
        query = """
        MATCH (w:Wallet {address: $address})
        OPTIONAL MATCH (w)-[out:SENT]->()
        OPTIONAL MATCH ()-[inp:SENT]->(w)
        OPTIONAL MATCH (w)-[:SENT]->(neighbor:Wallet)
        RETURN
            count(DISTINCT out) AS out_degree,
            count(DISTINCT inp) AS in_degree,
            count(DISTINCT neighbor) AS unique_neighbors,
            COALESCE(w.pagerank, 0.0) AS pagerank,
            COALESCE(w.fraud_score, 0.0) AS fraud_score
        """
        result = self.run_query(query, {"address": address})
        return result[0] if result else {}

    def get_subgraph_for_gnn(self, center: str, hops: int = 2, max_nodes: int = 500) -> dict:
        if not self._connected:
            return {"nodes": [], "edges": []}
        hops = max(1, min(hops, 10))
        node_query = f"""
        MATCH path = (center:Wallet {{address: $center}})-[:SENT*1..{hops}]-(neighbor:Wallet)
        WITH DISTINCT neighbor, length(path) AS dist
        ORDER BY dist
        LIMIT $limit
        RETURN neighbor.address AS address, neighbor.blockchain AS blockchain,
               COALESCE(neighbor.fraud_score, 0.0) AS fraud_score, dist
        """
        nodes = self.run_query(node_query, {"center": center, "limit": max_nodes})

        addresses = [center] + [n["address"] for n in nodes]
        edge_query = """
        MATCH (a:Wallet)-[r:SENT]->(b:Wallet)
        WHERE a.address IN $addresses AND b.address IN $addresses
        RETURN a.address AS source, b.address AS target, r.tx_hash AS tx_hash,
               r.amount AS amount, r.timestamp AS timestamp, r.blockchain AS blockchain
        """
        edges = self.run_query(edge_query, {"addresses": addresses})

        return {"nodes": nodes, "edges": edges}

    def get_wallet_transaction_history(self, address: str, limit: int = 100) -> list[dict]:
        if not self._connected:
            return []
        query = """
        MATCH (w:Wallet {address: $address})-[r:SENT]-(other:Wallet)
        RETURN w.address AS from_address, other.address AS to_address,
               r.tx_hash AS tx_hash, r.amount AS amount,
               r.timestamp AS timestamp, r.blockchain AS blockchain,
               CASE WHEN w.address = $address THEN 'outgoing' ELSE 'incoming' END AS direction
        ORDER BY r.timestamp DESC
        LIMIT $limit
        """
        return self.run_query(query, {"address": address, "limit": limit})

    def get_all_addresses(self, limit: int = 1000) -> list[str]:
        if not self._connected:
            return []
        result = self.run_query("MATCH (w:Wallet) RETURN w.address AS address LIMIT $limit", {"limit": limit})
        return [r["address"] for r in result]

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
