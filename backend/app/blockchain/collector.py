import time
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.blockchain.base import BlockchainAdapter, BlockchainSyncResult
from app.blockchain.ethereum import EthereumAdapter
from app.blockchain.bsc import BSCAdapter
from app.blockchain.normalizer import store_transactions, store_wallets
from app.blockchain.graph_builder import build_graph_from_transactions

logger = logging.getLogger(__name__)

ADAPTERS = {
    "ethereum": EthereumAdapter,
    "bnb": BSCAdapter,
}


def get_adapter(chain: str, api_key: str = "") -> Optional[BlockchainAdapter]:
    cls = ADAPTERS.get(chain)
    if cls:
        return cls(api_key=api_key)
    return None


class BlockchainCollector:
    """Orchestrates blockchain data collection: API → PostgreSQL → Neo4j."""

    def __init__(self, adapter: BlockchainAdapter):
        self.adapter = adapter

    async def sync_address(
        self, address: str, db: AsyncSession, max_pages: int = 5, page_size: int = 100
    ) -> BlockchainSyncResult:
        start = time.time()
        all_txs = []

        for page in range(1, max_pages + 1):
            txs = await self.adapter.get_transactions_by_address(
                address, page=page, offset=page_size
            )
            if not txs:
                break
            all_txs.extend(txs)
            if len(txs) < page_size:
                break

        stored_pg = await store_transactions(db, all_txs)
        wallets_stored = await store_wallets(db, all_txs, self.adapter.chain_name)
        graph_result = build_graph_from_transactions(all_txs)

        duration = round(time.time() - start, 2)
        return BlockchainSyncResult(
            blockchain=self.adapter.chain_name,
            transactions_found=len(all_txs),
            transactions_stored=stored_pg,
            wallets_found=wallets_stored,
            blocks_scanned=0,
            duration_seconds=duration,
        )

    async def sync_recent(
        self, db: AsyncSession, page: int = 1, offset: int = 100
    ) -> BlockchainSyncResult:
        start = time.time()
        try:
            latest_block = await self.adapter.get_latest_block()
        except Exception as e:
            return BlockchainSyncResult(
                blockchain=self.adapter.chain_name,
                transactions_found=0,
                transactions_stored=0,
                wallets_found=0,
                blocks_scanned=0,
                duration_seconds=0,
                error=str(e),
            )

        start_block = max(0, latest_block - 1000)
        all_txs = await self.adapter.get_transactions_by_page(
            address="0x0000000000000000000000000000000000000000",
            start_block=start_block,
            end_block=latest_block,
            page=page,
            offset=offset,
        )

        stored_pg = await store_transactions(db, all_txs)
        wallets_stored = await store_wallets(db, all_txs, self.adapter.chain_name)
        graph_result = build_graph_from_transactions(all_txs)

        duration = round(time.time() - start, 2)
        return BlockchainSyncResult(
            blockchain=self.adapter.chain_name,
            transactions_found=len(all_txs),
            transactions_stored=stored_pg,
            wallets_found=wallets_stored,
            blocks_scanned=latest_block - start_block,
            duration_seconds=duration,
        )
