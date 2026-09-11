from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.blockchain_config import BlockchainConfig
from app.blockchain.collector import get_adapter, BlockchainCollector

router = APIRouter()

CHAIN_DISPLAY_NAMES = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "bnb": "BNB Chain",
    "polygon": "Polygon",
    "tron": "Tron",
}

CHAIN_API_URLS = {
    "bitcoin": "https://blockstream.info/api",
    "ethereum": "https://api.etherscan.io/api",
    "bnb": "https://api.bscscan.com/api",
    "polygon": "https://api.polygonscan.com/api",
    "tron": "https://api.trongrid.io",
}


class BlockchainConfigUpdate(BaseModel):
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: Optional[bool] = None


async def _get_or_create_config(db: AsyncSession, chain: str) -> BlockchainConfig:
    result = await db.execute(
        select(BlockchainConfig).where(BlockchainConfig.blockchain == chain)
    )
    cfg = result.scalar_one_or_none()
    if not cfg:
        cfg = BlockchainConfig(
            blockchain=chain,
            display_name=CHAIN_DISPLAY_NAMES.get(chain, chain.title()),
            api_url=CHAIN_API_URLS.get(chain, ""),
            is_enabled=(chain in ("ethereum", "bnb")),
            sync_status="idle",
        )
        db.add(cfg)
        await db.commit()
        await db.refresh(cfg)
    return cfg


@router.get("/configs")
async def get_configs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlockchainConfig))
    configs = result.scalars().all()
    if not configs:
        for chain, name in CHAIN_DISPLAY_NAMES.items():
            await _get_or_create_config(db, chain)
        result = await db.execute(select(BlockchainConfig))
        configs = result.scalars().all()
    return [
        {
            "id": c.id,
            "blockchain": c.blockchain,
            "display_name": c.display_name,
            "api_url": c.api_url,
            "is_enabled": c.is_enabled,
            "last_sync": c.last_sync.isoformat() if c.last_sync else None,
            "tx_count": c.tx_count or 0,
            "wallet_count": c.wallet_count or 0,
            "block_height": c.block_height or 0,
            "sync_status": c.sync_status or "idle",
        }
        for c in configs
    ]


@router.get("/status")
async def get_status(db: AsyncSession = Depends(get_db)):
    return await get_configs(db)


@router.put("/configs/{chain}")
async def update_config(chain: str, data: BlockchainConfigUpdate, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db, chain)
    if data.api_url is not None:
        cfg.api_url = data.api_url
    if data.api_key is not None:
        cfg.api_key_encrypted = "***" + data.api_key[-4:] if len(data.api_key) > 4 else "***"
    if data.is_enabled is not None:
        cfg.is_enabled = data.is_enabled
        if not data.is_enabled:
            cfg.sync_status = "idle"
    db.add(cfg)
    await db.commit()
    await db.refresh(cfg)
    return {
        "id": cfg.id,
        "blockchain": cfg.blockchain,
        "display_name": cfg.display_name,
        "api_url": cfg.api_url,
        "is_enabled": cfg.is_enabled,
        "sync_status": cfg.sync_status,
    }


@router.post("/sync/{chain}")
async def sync_blockchain(chain: str, db: AsyncSession = Depends(get_db)):
    cfg = await _get_or_create_config(db, chain)
    adapter = get_adapter(chain)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"No adapter available for chain: {chain}")

    cfg.sync_status = "syncing"
    db.add(cfg)
    await db.commit()

    collector = BlockchainCollector(adapter)
    try:
        result = await collector.sync_recent(db)
        cfg.tx_count = (cfg.tx_count or 0) + result.transactions_stored
        cfg.wallet_count = (cfg.wallet_count or 0) + result.wallets_found
        cfg.block_height = (cfg.block_height or 0) + result.blocks_scanned
        cfg.last_sync = datetime.now(timezone.utc)
        cfg.sync_status = "synced" if not result.error else "error"
        db.add(cfg)
        await db.commit()
        return {
            "message": f"Sync completed for {chain}",
            "transactions_found": result.transactions_found,
            "transactions_stored": result.transactions_stored,
            "wallets_found": result.wallets_found,
            "blocks_scanned": result.blocks_scanned,
            "duration_seconds": result.duration_seconds,
            "error": result.error,
        }
    except Exception as e:
        cfg.sync_status = "error"
        db.add(cfg)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
