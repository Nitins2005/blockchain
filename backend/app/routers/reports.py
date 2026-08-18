from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta
from app.services.mock_data_service import get_fraud_prediction, get_wallet_explanation, generate_wallet_address, BLOCKCHAINS

router = APIRouter()

class ReportGenerate(BaseModel):
    wallet_address: str
    report_type: str = "wallet_analysis"
    investigation_id: Optional[int] = None

_reports = []

def _seed_reports():
    if not _reports:
        types = ["wallet_analysis", "investigation_summary", "fraud_assessment"]
        for i in range(8):
            blockchain = random.choice(BLOCKCHAINS)
            _reports.append({
                "id": i + 1,
                "wallet_address": generate_wallet_address(blockchain),
                "report_type": random.choice(types),
                "investigation_id": random.randint(1, 10) if random.random() > 0.5 else None,
                "fraud_score": round(random.uniform(0.1, 0.99), 3),
                "risk_level": random.choice(["low", "medium", "high", "critical"]),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
                "pdf_available": True
            })

_seed_reports()

@router.get("")
async def list_reports():
    return {"items": _reports, "total": len(_reports)}

@router.post("/generate")
async def generate_report(data: ReportGenerate):
    new_id = max((r["id"] for r in _reports), default=0) + 1
    fraud = get_fraud_prediction(data.wallet_address)
    report = {
        "id": new_id,
        "wallet_address": data.wallet_address,
        "report_type": data.report_type,
        "investigation_id": data.investigation_id,
        "fraud_score": fraud["fraud_score"],
        "risk_level": fraud["risk_level"],
        "created_at": datetime.utcnow().isoformat(),
        "pdf_available": True
    }
    _reports.append(report)
    return report

@router.get("/{report_id}/download")
async def download_report(report_id: int):
    report = next((r for r in _reports if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    try:
        from app.utils.pdf_generator import generate_investigation_report
        wallet_data = {
            "address": report["wallet_address"],
            "blockchain": random.choice(BLOCKCHAINS),
            "category": "Unknown",
            "tx_count": random.randint(10, 5000),
            "balance": round(random.uniform(0, 100), 6),
            "last_active": datetime.utcnow().isoformat()
        }
        fraud_data = get_fraud_prediction(report["wallet_address"])
        explanation_data = get_wallet_explanation(report["wallet_address"])
        pdf_bytes = generate_investigation_report(wallet_data, fraud_data, explanation_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=cryptoshield_report_{report_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
