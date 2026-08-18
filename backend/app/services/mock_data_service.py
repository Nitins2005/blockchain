import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any

BLOCKCHAINS = ["bitcoin", "ethereum", "bnb", "polygon", "tron"]
WALLET_CATEGORIES = ["Exchange", "Mining Pool", "Scam Wallet", "Darknet Wallet", "Mixer", "Bridge", "DeFi Protocol", "NFT Marketplace", "Personal Wallet", "Unknown"]
RISK_LEVELS = ["low", "medium", "high", "critical"]
TOKENS = ["BTC", "ETH", "BNB", "MATIC", "TRX", "USDT", "USDC", "WETH", "LINK", "UNI"]

def generate_wallet_address(blockchain: str) -> str:
    prefix = {"bitcoin": "1", "ethereum": "0x", "bnb": "0x", "polygon": "0x", "tron": "T"}.get(blockchain, "0x")
    rand_hex = hashlib.sha256(str(random.random()).encode()).hexdigest()
    if prefix in ["0x"]:
        return f"0x{rand_hex[:40]}"
    elif prefix == "1":
        return f"1{rand_hex[:33]}"
    else:
        return f"T{rand_hex[:33]}"

def get_fraud_prediction(wallet_address: str) -> Dict[str, Any]:
    seed = sum(ord(c) for c in wallet_address)
    random.seed(seed)
    fraud_score = round(random.uniform(0.05, 0.98), 4)
    if fraud_score < 0.3:
        risk_level = "low"
    elif fraud_score < 0.6:
        risk_level = "medium"
    elif fraud_score < 0.8:
        risk_level = "high"
    else:
        risk_level = "critical"
    confidence = round(random.uniform(0.72, 0.98), 4)
    tx_count = random.randint(5, 5000)
    connected_wallets = random.randint(2, 200)
    last_activity = datetime.utcnow() - timedelta(days=random.randint(0, 365))
    random.seed()
    return {
        "wallet_address": wallet_address,
        "fraud_score": fraud_score,
        "risk_level": risk_level,
        "confidence": confidence,
        "last_activity": last_activity.isoformat(),
        "tx_count": tx_count,
        "connected_wallets": connected_wallets,
        "cross_chain_activity": random.random() > 0.5,
        "prediction_time": datetime.utcnow().isoformat(),
        "model_version": "mock-v1.0.0"
    }

def get_wallet_attribution(wallet_address: str) -> Dict[str, Any]:
    seed = sum(ord(c) for c in wallet_address) + 42
    random.seed(seed)
    primary_category = random.choice(WALLET_CATEGORIES)
    confidence = round(random.uniform(0.6, 0.97), 4)
    secondary = random.sample([c for c in WALLET_CATEGORIES if c != primary_category], k=2)
    secondary_categories = [{"category": cat, "confidence": round(random.uniform(0.05, 0.4), 3)} for cat in secondary]
    random.seed()
    return {
        "wallet_address": wallet_address,
        "category": primary_category,
        "confidence": confidence,
        "secondary_categories": secondary_categories,
        "prediction_time": datetime.utcnow().isoformat(),
        "model_version": "mock-v1.0.0"
    }

def get_wallet_explanation(wallet_address: str) -> Dict[str, Any]:
    seed = sum(ord(c) for c in wallet_address) + 99
    random.seed(seed)
    features = [
        {"name": "Degree Centrality", "importance": round(random.uniform(0.6, 0.95), 3), "value": round(random.uniform(0.01, 0.9), 3)},
        {"name": "Transaction Frequency", "importance": round(random.uniform(0.5, 0.9), 3), "value": random.randint(10, 5000)},
        {"name": "Average TX Amount", "importance": round(random.uniform(0.4, 0.85), 3), "value": round(random.uniform(0.001, 100), 4)},
        {"name": "Cross-Chain Activity", "importance": round(random.uniform(0.3, 0.8), 3), "value": random.randint(0, 50)},
        {"name": "Betweenness Centrality", "importance": round(random.uniform(0.2, 0.75), 3), "value": round(random.uniform(0, 0.5), 4)},
        {"name": "Clustering Coefficient", "importance": round(random.uniform(0.2, 0.7), 3), "value": round(random.uniform(0, 1), 4)},
        {"name": "Token Diversity", "importance": round(random.uniform(0.15, 0.65), 3), "value": random.randint(1, 20)},
        {"name": "PageRank Score", "importance": round(random.uniform(0.1, 0.6), 3), "value": round(random.uniform(0, 0.01), 6)},
    ]
    features.sort(key=lambda x: x["importance"], reverse=True)
    risk_factors_pool = [
        "Connected to multiple blacklisted wallets",
        "High transaction frequency anomaly detected",
        "Cross-chain movement pattern matches mixer behavior",
        "Abnormal transfer amounts (round numbers)",
        "Interaction with known malicious smart contracts",
        "Funds received from flagged exchange withdrawal",
        "Rapid layering of transactions detected",
        "Low time-delta between incoming and outgoing transfers",
    ]
    risk_factors = random.sample(risk_factors_pool, k=random.randint(2, 5))
    neighbor_influence = []
    for i in range(3):
        addr = generate_wallet_address("ethereum")
        neighbor_influence.append({"address": addr, "influence_score": round(random.uniform(0.1, 0.9), 3), "is_blacklisted": random.random() > 0.6})
    temporal_activity = []
    base_date = datetime.utcnow() - timedelta(days=30)
    for day in range(30):
        date = base_date + timedelta(days=day)
        temporal_activity.append({"date": date.strftime("%Y-%m-%d"), "tx_count": random.randint(0, 50), "volume": round(random.uniform(0, 100), 4)})
    important_txs = []
    for i in range(3):
        important_txs.append({
            "tx_hash": f"0x{hashlib.md5(str(random.random()).encode()).hexdigest()}",
            "amount": round(random.uniform(0.1, 1000), 4),
            "blockchain": random.choice(BLOCKCHAINS),
            "importance": round(random.uniform(0.5, 1.0), 3),
            "timestamp": (datetime.utcnow() - timedelta(days=random.randint(1, 60))).isoformat()
        })
    fraud_score = get_fraud_prediction(wallet_address)["fraud_score"]
    reasoning_parts = []
    if fraud_score > 0.7:
        reasoning_parts.append(f"This wallet exhibits HIGH-RISK behavior with a fraud score of {fraud_score:.1%}.")
    elif fraud_score > 0.4:
        reasoning_parts.append(f"This wallet shows MODERATE-RISK indicators with a fraud score of {fraud_score:.1%}.")
    else:
        reasoning_parts.append(f"This wallet appears LOW-RISK with a fraud score of {fraud_score:.1%}.")
    reasoning_parts.append(f"Key contributing factors include: {', '.join(risk_factors[:2])}.")
    reasoning_parts.append(f"The GNN model analyzed {len(features)} temporal graph features and {len(neighbor_influence)} neighbor wallets to arrive at this conclusion.")
    random.seed()
    return {
        "wallet_address": wallet_address,
        "top_features": features,
        "neighbor_influence": neighbor_influence,
        "important_transactions": important_txs,
        "temporal_activity": temporal_activity,
        "risk_factors": risk_factors,
        "reasoning_text": " ".join(reasoning_parts),
        "fraud_score": fraud_score
    }

def generate_mock_transactions(count: int = 50, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    transactions = []
    base_time = datetime.utcnow()
    for i in range(count):
        blockchain = random.choice(BLOCKCHAINS)
        tx_hash = f"0x{hashlib.sha256(str(i + random.random()).encode()).hexdigest()[:64]}"
        amount = round(random.uniform(0.001, 10000), 6)
        transactions.append({
            "id": i + 1,
            "tx_hash": tx_hash,
            "sender_address": generate_wallet_address(blockchain),
            "receiver_address": generate_wallet_address(blockchain),
            "blockchain": blockchain,
            "amount": amount,
            "amount_usd": round(amount * random.uniform(100, 50000), 2),
            "gas_fee": round(random.uniform(0.00001, 0.01), 8),
            "token": random.choice(TOKENS),
            "block_number": random.randint(1000000, 50000000),
            "timestamp": (base_time - timedelta(hours=random.randint(0, 8760))).isoformat(),
            "status": random.choice(["confirmed", "confirmed", "confirmed", "pending", "failed"]),
            "is_flagged": random.random() > 0.85
        })
    total = count
    start = (page - 1) * page_size
    end = start + page_size
    return {"items": transactions[start:end], "total": total, "page": page, "page_size": page_size, "pages": (total + page_size - 1) // page_size}

def generate_mock_wallets(count: int = 30) -> List[Dict[str, Any]]:
    wallets = []
    for i in range(count):
        blockchain = random.choice(BLOCKCHAINS)
        address = generate_wallet_address(blockchain)
        fraud_score = round(random.uniform(0, 1), 4)
        risk_level = "low" if fraud_score < 0.3 else "medium" if fraud_score < 0.6 else "high" if fraud_score < 0.8 else "critical"
        wallets.append({
            "id": i + 1,
            "address": address,
            "blockchain": blockchain,
            "tx_count": random.randint(1, 10000),
            "balance": round(random.uniform(0, 1000), 6),
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "category": random.choice(WALLET_CATEGORIES),
            "is_blacklisted": random.random() > 0.9,
            "last_active": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat()
        })
    return wallets

def generate_dashboard_stats() -> Dict[str, Any]:
    base = datetime.utcnow()
    fraud_trend = []
    for i in range(30):
        date = base - timedelta(days=29 - i)
        fraud_trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "flagged": random.randint(5, 80),
            "total": random.randint(200, 2000),
            "score_avg": round(random.uniform(0.2, 0.6), 3)
        })
    volume_trend = []
    for i in range(14):
        date = base - timedelta(days=13 - i)
        btc = round(random.uniform(1000, 50000), 2)
        eth = round(random.uniform(500, 30000), 2)
        bnb = round(random.uniform(200, 10000), 2)
        poly = round(random.uniform(100, 5000), 2)
        tron = round(random.uniform(50, 3000), 2)
        volume_trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "volume": round(btc + eth + bnb + poly + tron, 2),
            "bitcoin": btc,
            "ethereum": eth,
            "bnb": bnb,
            "polygon": poly,
            "tron": tron
        })
    return {
        "total_wallets": random.randint(45000, 80000),
        "fraudulent_wallets": random.randint(1200, 3500),
        "total_transactions": random.randint(500000, 2000000),
        "blockchain_networks": 5,
        "active_investigations": random.randint(12, 45),
        "avg_fraud_score": round(random.uniform(0.2, 0.45), 3),
        "fraud_trend": fraud_trend,
        "volume_trend": volume_trend,
        "blockchain_distribution": [
            {"name": "Bitcoin", "value": random.randint(20, 35)},
            {"name": "Ethereum", "value": random.randint(25, 40)},
            {"name": "BNB Chain", "value": random.randint(10, 20)},
            {"name": "Polygon", "value": random.randint(8, 15)},
            {"name": "Tron", "value": random.randint(5, 12)}
        ],
        "wallet_category_distribution": [
            {"name": cat, "value": random.randint(50, 500)}
            for cat in WALLET_CATEGORIES
        ],
        "top_suspicious_wallets": generate_mock_wallets(5)
    }
