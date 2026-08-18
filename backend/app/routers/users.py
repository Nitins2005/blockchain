from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import random
from datetime import datetime, timedelta

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    role: str = "investigator"
    department: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None

_users = [
    {"id": 1, "email": "admin@cryptoshield.ai", "username": "admin",
     "full_name": "System Administrator", "role": "admin", "is_active": True,
     "department": "IT Security",
     "created_at": (datetime.utcnow() - timedelta(days=180)).isoformat(),
     "last_login": datetime.utcnow().isoformat()},
    {"id": 2, "email": "investigator@cryptoshield.ai", "username": "investigator",
     "full_name": "Lead Investigator", "role": "investigator", "is_active": True,
     "department": "Fraud Analysis",
     "created_at": (datetime.utcnow() - timedelta(days=90)).isoformat(),
     "last_login": (datetime.utcnow() - timedelta(hours=2)).isoformat()},
] + [
    {"id": i+3, "email": f"analyst{i+1}@cryptoshield.ai", "username": f"analyst{i+1}",
     "full_name": f"Analyst {i+1}", "role": "investigator", "is_active": random.random() > 0.2,
     "department": random.choice(["Fraud Analysis", "Compliance", "Risk Management"]),
     "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat(),
     "last_login": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat()}
    for i in range(8)
]

@router.get("")
async def list_users(
    page: int = 1, page_size: int = 20,
    role: Optional[str] = None, search: Optional[str] = None, is_active: Optional[bool] = None
):
    items = _users.copy()
    if role:
        items = [u for u in items if u["role"] == role]
    if search:
        items = [u for u in items if search.lower() in u["email"].lower() or search.lower() in u["full_name"].lower()]
    if is_active is not None:
        items = [u for u in items if u["is_active"] == is_active]
    total = len(items)
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "total": total, "page": page, "page_size": page_size}

@router.get("/stats")
async def get_user_stats():
    return {
        "total": len(_users), "active": sum(1 for u in _users if u["is_active"]),
        "admins": sum(1 for u in _users if u["role"] == "admin"),
        "investigators": sum(1 for u in _users if u["role"] == "investigator")
    }

@router.get("/{user_id}")
async def get_user(user_id: int):
    for u in _users:
        if u["id"] == user_id:
            return u
    raise HTTPException(status_code=404, detail="User not found")

@router.post("")
async def create_user(data: UserCreate):
    new_id = max(u["id"] for u in _users) + 1
    user = {"id": new_id, "email": data.email, "username": data.username,
             "full_name": data.full_name, "role": data.role, "is_active": True,
             "department": data.department,
             "created_at": datetime.utcnow().isoformat(), "last_login": None}
    _users.append(user)
    return user

@router.put("/{user_id}")
async def update_user(user_id: int, data: UserUpdate):
    for u in _users:
        if u["id"] == user_id:
            if data.full_name is not None: u["full_name"] = data.full_name
            if data.department is not None: u["department"] = data.department
            if data.is_active is not None: u["is_active"] = data.is_active
            if data.role is not None: u["role"] = data.role
            return u
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    global _users
    _users = [u for u in _users if u["id"] != user_id]
    return {"message": "User deleted"}
