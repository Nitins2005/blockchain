from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.wallet_feature import WalletFeature
from app.services.graph_service import (
    compute_wallet_features,
    compute_all_features,
    get_feature_vector,
    FEATURE_NAMES,
)

router = APIRouter()


@router.get("/wallet/{address}")
async def get_wallet_features(address: str, blockchain: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WalletFeature).where(WalletFeature.wallet_address == address.lower())
    )
    wf = result.scalar_one_or_none()
    if not wf:
        wf = await compute_wallet_features(db, address, blockchain or "ethereum")

    from datetime import datetime, timezone
    return {
        "id": wf.id,
        "wallet_address": wf.wallet_address,
        "blockchain": wf.blockchain,
        "incoming_tx": wf.incoming_tx,
        "outgoing_tx": wf.outgoing_tx,
        "avg_tx_amount": wf.avg_tx_amount,
        "max_tx_amount": wf.max_tx_amount,
        "balance": wf.balance,
        "active_days": wf.active_days,
        "gas_usage": wf.gas_usage,
        "token_diversity": wf.token_diversity,
        "neighbor_count": wf.neighbor_count,
        "degree_centrality": wf.degree_centrality,
        "betweenness_centrality": wf.betweenness_centrality,
        "pagerank": wf.pagerank,
        "clustering_coefficient": wf.clustering_coefficient,
        "cross_chain_tx_count": wf.cross_chain_tx_count,
        "computed_at": wf.computed_at.isoformat() if wf.computed_at else datetime.now(timezone.utc).isoformat(),
    }


@router.get("/vector/{address}")
async def get_feature_vector_endpoint(address: str, blockchain: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WalletFeature).where(WalletFeature.wallet_address == address.lower())
    )
    wf = result.scalar_one_or_none()
    if not wf:
        wf = await compute_wallet_features(db, address, blockchain or "ethereum")
    return get_feature_vector(wf)


@router.post("/compute/{address}")
async def compute_features(address: str, blockchain: Optional[str] = None, include_graph: bool = True, db: AsyncSession = Depends(get_db)):
    wf = await compute_wallet_features(db, address, blockchain or "ethereum", include_graph=include_graph)
    return {
        "message": "Features computed successfully",
        "features": {
            "wallet_address": wf.wallet_address,
            "blockchain": wf.blockchain,
            "incoming_tx": wf.incoming_tx,
            "outgoing_tx": wf.outgoing_tx,
            "avg_tx_amount": wf.avg_tx_amount,
            "max_tx_amount": wf.max_tx_amount,
            "balance": wf.balance,
            "active_days": wf.active_days,
            "gas_usage": wf.gas_usage,
            "token_diversity": wf.token_diversity,
            "neighbor_count": wf.neighbor_count,
            "degree_centrality": wf.degree_centrality,
            "betweenness_centrality": wf.betweenness_centrality,
            "pagerank": wf.pagerank,
            "clustering_coefficient": wf.clustering_coefficient,
            "cross_chain_tx_count": wf.cross_chain_tx_count,
        },
    }


@router.post("/compute-all")
async def compute_all_features_endpoint(blockchain: Optional[str] = None, include_graph: bool = True, db: AsyncSession = Depends(get_db)):
    count = await compute_all_features(db, blockchain, include_graph)
    return {"message": f"Computed features for {count} wallets", "wallets_processed": count}


@router.get("/feature-names")
async def get_feature_names():
    return {"feature_names": FEATURE_NAMES, "count": len(FEATURE_NAMES)}
