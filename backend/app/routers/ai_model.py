from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import uuid
import random
from datetime import datetime
from app.services.mock_data_service import (
    get_fraud_prediction, get_wallet_attribution, get_wallet_explanation
)

router = APIRouter()

class WalletRequest(BaseModel):
    wallet_address: str
    blockchain: Optional[str] = None

class TransactionRequest(BaseModel):
    tx_hash: str
    blockchain: Optional[str] = None

@router.post("/train-model")
async def train_model():
    return {
        "status": "training_started",
        "job_id": str(uuid.uuid4()),
        "estimated_duration_minutes": random.randint(15, 120),
        "model_type": "Temporal-GNN",
        "dataset_size": random.randint(50000, 500000),
        "started_at": datetime.utcnow().isoformat(),
        "message": "Model training has been initiated. Connect the Python GNN pipeline to replace this mock."
    }

@router.post("/predict-wallet")
async def predict_wallet(req: WalletRequest):
    return get_fraud_prediction(req.wallet_address)

@router.post("/predict-transaction")
async def predict_transaction(req: TransactionRequest):
    seed = sum(ord(c) for c in req.tx_hash)
    random.seed(seed)
    score = round(random.uniform(0.01, 0.99), 4)
    random.seed()
    return {
        "tx_hash": req.tx_hash,
        "anomaly_score": score,
        "is_anomalous": score > 0.7,
        "confidence": round(random.uniform(0.7, 0.99), 4),
        "prediction_time": datetime.utcnow().isoformat(),
        "model_version": "mock-v1.0.0"
    }

@router.post("/wallet-attribution")
async def wallet_attribution(req: WalletRequest):
    return get_wallet_attribution(req.wallet_address)

@router.post("/explain-wallet")
async def explain_wallet(req: WalletRequest):
    return get_wallet_explanation(req.wallet_address)

@router.get("/model-status")
async def model_status():
    return {
        "model_version": "mock-v1.0.0",
        "model_type": "Temporal Explainable Multi-Chain GNN",
        "status": "ready",
        "last_trained": (datetime.utcnow()).isoformat(),
        "training_dataset_size": 250000,
        "supported_chains": ["bitcoin", "ethereum", "bnb", "polygon", "tron"],
        "metrics": {
            "accuracy": 0.9421,
            "precision": 0.9187,
            "recall": 0.8934,
            "f1_score": 0.9059,
            "auc_roc": 0.9673
        },
        "note": "Running in mock mode. Connect the Python Temporal GNN pipeline to enable real predictions."
    }

@router.get("/training-progress")
async def training_progress():
    epoch = random.randint(1, 100)
    return {
        "status": "idle",
        "epoch": epoch,
        "total_epochs": 100,
        "loss": round(random.uniform(0.01, 0.5), 4),
        "accuracy": round(random.uniform(0.7, 0.99), 4),
        "val_loss": round(random.uniform(0.02, 0.6), 4),
        "val_accuracy": round(random.uniform(0.65, 0.98), 4),
        "progress_percent": epoch,
        "eta_minutes": random.randint(0, 60)
    }
