from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.investigation import Investigation, InvestigationWallet, InvestigationNote
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


class InvestigationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assigned_to_id: Optional[int] = None


class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[int] = None


class NoteCreate(BaseModel):
    content: str


class WalletAttach(BaseModel):
    wallet_address: str
    blockchain: str


@router.get("")
async def list_investigations(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Investigation)
    if status:
        query = query.where(Investigation.status == status)
    if priority:
        query = query.where(Investigation.priority == priority)
    query = query.order_by(Investigation.created_at.desc())

    from sqlalchemy import func

    count_query = select(func.count()).select_from(Investigation)
    if status:
        count_query = count_query.where(Investigation.status == status)
    if priority:
        count_query = count_query.where(Investigation.priority == priority)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    enriched = []
    for inv in items:
        wallet_count_result = await db.execute(
            select(func.count())
            .select_from(InvestigationWallet)
            .where(InvestigationWallet.investigation_id == inv.id)
        )
        wallet_count = wallet_count_result.scalar()
        enriched.append({
            "id": inv.id,
            "title": inv.title,
            "description": inv.description,
            "status": inv.status.value if inv.status else "open",
            "priority": inv.priority,
            "created_by_id": inv.created_by_id,
            "assigned_to_id": inv.assigned_to_id,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
            "wallet_count": wallet_count,
        })

    return {"items": enriched, "total": total, "page": page, "page_size": page_size}


@router.get("/{inv_id}")
async def get_investigation(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Investigation).where(Investigation.id == inv_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    wallet_count_result = await db.execute(
        select(func.count())
        .select_from(InvestigationWallet)
        .where(InvestigationWallet.investigation_id == inv.id)
    )
    wallet_count = wallet_count_result.scalar()

    return {
        "id": inv.id,
        "title": inv.title,
        "description": inv.description,
        "status": inv.status.value if inv.status else "open",
        "priority": inv.priority,
        "created_by_id": inv.created_by_id,
        "assigned_to_id": inv.assigned_to_id,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
        "wallet_count": wallet_count,
    }


@router.post("")
async def create_investigation(
    data: InvestigationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = Investigation(
        title=data.title,
        description=data.description,
        priority=data.priority,
        created_by_id=current_user.id,
        assigned_to_id=data.assigned_to_id,
    )
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return {
        "id": inv.id,
        "title": inv.title,
        "description": inv.description,
        "status": inv.status.value if inv.status else "open",
        "priority": inv.priority,
        "created_by_id": inv.created_by_id,
        "assigned_to_id": inv.assigned_to_id,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }


@router.put("/{inv_id}")
async def update_investigation(
    inv_id: int,
    data: InvestigationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Investigation).where(Investigation.id == inv_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    if data.title is not None:
        inv.title = data.title
    if data.description is not None:
        inv.description = data.description
    if data.status is not None:
        inv.status = data.status
    if data.priority is not None:
        inv.priority = data.priority
    if data.assigned_to_id is not None:
        inv.assigned_to_id = data.assigned_to_id

    await db.commit()
    await db.refresh(inv)
    return {
        "id": inv.id,
        "title": inv.title,
        "description": inv.description,
        "status": inv.status.value if inv.status else "open",
        "priority": inv.priority,
        "created_by_id": inv.created_by_id,
        "assigned_to_id": inv.assigned_to_id,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }


@router.delete("/{inv_id}")
async def delete_investigation(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Investigation).where(Investigation.id == inv_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    await db.execute(delete(InvestigationNote).where(InvestigationNote.investigation_id == inv_id))
    await db.execute(delete(InvestigationWallet).where(InvestigationWallet.investigation_id == inv_id))
    await db.delete(inv)
    await db.commit()
    return {"message": "Investigation deleted"}


@router.get("/{inv_id}/wallets")
async def get_investigation_wallets(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InvestigationWallet).where(InvestigationWallet.investigation_id == inv_id)
    )
    wallets = result.scalars().all()
    return [
        {
            "id": w.id,
            "investigation_id": w.investigation_id,
            "wallet_address": w.wallet_address,
            "blockchain": w.blockchain,
            "added_at": w.added_at.isoformat() if w.added_at else None,
        }
        for w in wallets
    ]


@router.post("/{inv_id}/wallets")
async def attach_wallet(
    inv_id: int,
    data: WalletAttach,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Investigation).where(Investigation.id == inv_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    wallet = InvestigationWallet(
        investigation_id=inv_id,
        wallet_address=data.wallet_address,
        blockchain=data.blockchain,
    )
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return {
        "id": wallet.id,
        "investigation_id": wallet.investigation_id,
        "wallet_address": wallet.wallet_address,
        "blockchain": wallet.blockchain,
        "added_at": wallet.added_at.isoformat() if wallet.added_at else None,
    }


@router.delete("/{inv_id}/wallets/{wallet_address}")
async def remove_wallet(
    inv_id: int,
    wallet_address: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        delete(InvestigationWallet).where(
            InvestigationWallet.investigation_id == inv_id,
            InvestigationWallet.wallet_address == wallet_address,
        )
    )
    await db.commit()
    return {"message": "Wallet removed"}


@router.get("/{inv_id}/notes")
async def get_notes(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InvestigationNote)
        .where(InvestigationNote.investigation_id == inv_id)
        .order_by(InvestigationNote.created_at.desc())
    )
    notes = result.scalars().all()
    return [
        {
            "id": n.id,
            "investigation_id": n.investigation_id,
            "content": n.content,
            "author_id": n.author_id,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notes
    ]


@router.post("/{inv_id}/notes")
async def add_note(
    inv_id: int,
    data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Investigation).where(Investigation.id == inv_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    note = InvestigationNote(
        investigation_id=inv_id,
        content=data.content,
        author_id=current_user.id,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return {
        "id": note.id,
        "investigation_id": note.investigation_id,
        "content": note.content,
        "author_id": note.author_id,
        "created_at": note.created_at.isoformat() if note.created_at else None,
    }


@router.post("/{inv_id}/generate-report")
async def generate_report(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Investigation).where(Investigation.id == inv_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    return {
        "message": "Report generation started",
        "investigation_id": inv_id,
        "report_id": inv_id,
        "eta_seconds": 5,
    }
