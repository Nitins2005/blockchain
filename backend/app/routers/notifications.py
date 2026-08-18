from fastapi import APIRouter, HTTPException
from typing import Optional
import random
from datetime import datetime, timedelta

router = APIRouter()

_notifications = []

def _seed_notifications():
    if not _notifications:
        types_messages = [
            ("fraud_detected", "High-Risk Wallet Detected", "Wallet 0x4a2b...c891 scored 0.94 fraud score"),
            ("model_trained", "Model Training Complete", "Temporal GNN v1.0 finished training with 94.2% accuracy"),
            ("new_investigation", "New Investigation Created", "Investigation #11: DeFi Exploit opened"),
            ("wallet_blacklisted", "Wallet Added to Blacklist", "Address 0xde4f... added to mixer category"),
            ("high_risk_found", "Critical Risk Wallet", "Wallet T8xK2... linked to darknet marketplace"),
            ("fraud_detected", "Suspicious Activity", "Unusual transaction volume on BNB Chain wallet"),
            ("new_investigation", "Case Assigned", "Investigation #8 assigned to you"),
            ("wallet_blacklisted", "Blacklist Update", "15 new scam wallets imported from OFAC list"),
        ]
        for i, (ntype, title, msg) in enumerate(types_messages):
            _notifications.append({
                "id": i + 1,
                "user_id": 1,
                "type": ntype,
                "title": title,
                "message": msg,
                "is_read": i > 3,
                "created_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 168))).isoformat()
            })

_seed_notifications()

@router.get("")
async def get_notifications(unread_only: bool = False):
    items = _notifications.copy()
    if unread_only:
        items = [n for n in items if not n["is_read"]]
    return {"items": sorted(items, key=lambda x: x["created_at"], reverse=True), "total": len(items)}

@router.get("/unread-count")
async def get_unread_count():
    count = sum(1 for n in _notifications if not n["is_read"])
    return {"count": count}

@router.put("/{notif_id}/read")
async def mark_read(notif_id: int):
    for n in _notifications:
        if n["id"] == notif_id:
            n["is_read"] = True
            return n
    raise HTTPException(status_code=404, detail="Notification not found")

@router.post("/mark-all-read")
async def mark_all_read():
    for n in _notifications:
        n["is_read"] = True
    return {"message": "All notifications marked as read"}

@router.delete("/{notif_id}")
async def delete_notification(notif_id: int):
    global _notifications
    _notifications = [n for n in _notifications if n["id"] != notif_id]
    return {"message": "Notification deleted"}
