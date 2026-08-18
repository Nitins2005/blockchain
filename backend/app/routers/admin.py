from fastapi import APIRouter
from app.services.mock_data_service import (
    generate_dashboard_stats, generate_mock_wallets, generate_mock_transactions
)
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats")
async def get_stats():
    return generate_dashboard_stats()

@router.get("/fraud-trend")
async def get_fraud_trend():
    base = datetime.utcnow()
    return [
        {
            "date": (base - timedelta(days=29-i)).strftime("%Y-%m-%d"),
            "flagged": random.randint(5, 80),
            "total": random.randint(200, 2000),
            "score_avg": round(random.uniform(0.2, 0.6), 3)
        }
        for i in range(30)
    ]

@router.get("/volume-trend")
async def get_volume_trend():
    base = datetime.utcnow()
    return [
        {
            "date": (base - timedelta(days=13-i)).strftime("%Y-%m-%d"),
            "bitcoin": round(random.uniform(1000, 50000), 2),
            "ethereum": round(random.uniform(500, 30000), 2),
            "bnb": round(random.uniform(200, 10000), 2),
            "polygon": round(random.uniform(100, 5000), 2),
            "tron": round(random.uniform(50, 3000), 2)
        }
        for i in range(14)
    ]

@router.get("/blockchain-distribution")
async def get_blockchain_distribution():
    return [
        {"name": "Bitcoin", "value": random.randint(20, 35)},
        {"name": "Ethereum", "value": random.randint(25, 40)},
        {"name": "BNB Chain", "value": random.randint(10, 20)},
        {"name": "Polygon", "value": random.randint(8, 15)},
        {"name": "Tron", "value": random.randint(5, 12)}
    ]

@router.get("/category-distribution")
async def get_category_distribution():
    categories = ["Exchange", "Mining Pool", "Scam Wallet", "Darknet Wallet",
                  "Mixer", "Bridge", "DeFi Protocol", "NFT Marketplace", "Personal Wallet", "Unknown"]
    return [{"name": cat, "value": random.randint(50, 500)} for cat in categories]

@router.get("/recent-investigations")
async def get_recent_investigations():
    statuses = ["open", "in_progress", "closed"]
    priorities = ["critical", "high", "medium", "low"]
    return [
        {
            "id": i + 1,
            "title": f"Investigation #{i+1}: Suspicious Wallet Cluster",
            "status": random.choice(statuses),
            "priority": random.choice(priorities),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
            "wallet_count": random.randint(1, 20)
        }
        for i in range(10)
    ]

@router.get("/system-health")
async def get_system_health():
    return {
        "api_status": "operational",
        "database_status": "connected",
        "neo4j_status": "connected",
        "model_status": "ready",
        "uptime_seconds": random.randint(10000, 1000000),
        "total_requests": random.randint(5000, 50000),
        "avg_response_ms": round(random.uniform(20, 150), 1),
        "memory_usage_mb": round(random.uniform(200, 800), 1),
        "cpu_usage_percent": round(random.uniform(5, 40), 1)
    }
