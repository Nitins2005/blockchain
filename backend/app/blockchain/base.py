from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class NormalizedTransaction:
    tx_hash: str
    sender_address: str
    receiver_address: str
    blockchain: str
    amount: float
    amount_usd: Optional[float]
    gas_fee: Optional[float]
    gas_fee_usd: Optional[float]
    token: str
    block_number: Optional[int]
    timestamp: datetime
    status: str = "confirmed"
    is_flagged: bool = False


@dataclass
class BlockchainSyncResult:
    blockchain: str
    transactions_found: int
    transactions_stored: int
    wallets_found: int
    blocks_scanned: int
    duration_seconds: float
    error: Optional[str] = None


class BlockchainAdapter(ABC):
    """Base class for blockchain data collection adapters."""

    @property
    @abstractmethod
    def chain_name(self) -> str:
        pass

    @property
    @abstractmethod
    def native_token(self) -> str:
        pass

    @abstractmethod
    async def get_latest_block(self) -> int:
        pass

    @abstractmethod
    async def get_transactions_by_address(
        self, address: str, page: int = 1, offset: int = 100
    ) -> List[NormalizedTransaction]:
        pass

    @abstractmethod
    async def get_transactions_by_page(
        self, address: str, start_block: int, end_block: int, page: int = 1, offset: int = 100
    ) -> List[NormalizedTransaction]:
        pass

    @abstractmethod
    async def get_transaction_details(self, tx_hash: str) -> Optional[NormalizedTransaction]:
        pass
