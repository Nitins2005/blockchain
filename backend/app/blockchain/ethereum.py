import httpx
import logging
from typing import List, Optional
from datetime import datetime, timezone
from app.blockchain.base import BlockchainAdapter, NormalizedTransaction
from app.config import settings

logger = logging.getLogger(__name__)

ETHERSCAN_API_URL = "https://api.etherscan.io/api"


class EthereumAdapter(BlockchainAdapter):

    def __init__(self, api_key: str = ""):
        self._api_key = api_key or settings.ETHERSCAN_API_KEY
        self._base_url = ETHERSCAN_API_URL

    @property
    def chain_name(self) -> str:
        return "ethereum"

    @property
    def native_token(self) -> str:
        return "ETH"

    def _params(self, **kwargs) -> dict:
        params = {"apikey": self._api_key, **kwargs}
        return params

    async def _request(self, **kwargs) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(self._base_url, params=self._params(**kwargs))
            resp.raise_for_status()
            return resp.json()

    def _parse_tx(self, raw: dict) -> NormalizedTransaction:
        value_wei = int(raw.get("value", "0"))
        amount = value_wei / 1e18

        gas_used = int(raw.get("gasUsed", "0"))
        gas_price = int(raw.get("gasPrice", "0"))
        gas_fee = (gas_used * gas_price) / 1e18

        ts = int(raw.get("timeStamp", "0"))
        timestamp = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else datetime.now(timezone.utc)

        status = "confirmed" if raw.get("txreceipt_status") == "1" else "failed"

        return NormalizedTransaction(
            tx_hash=raw["hash"],
            sender_address=raw["from"].lower(),
            receiver_address=raw["to"].lower() if raw.get("to") else "",
            blockchain="ethereum",
            amount=round(amount, 8),
            amount_usd=None,
            gas_fee=round(gas_fee, 10),
            gas_fee_usd=None,
            token="ETH",
            block_number=int(raw.get("blockNumber", 0)),
            timestamp=timestamp,
            status=status,
            is_flagged=False,
        )

    async def get_latest_block(self) -> int:
        data = await self._request(module="proxy", action="eth_blockNumber")
        return int(data["result"], 16)

    async def get_transactions_by_address(
        self, address: str, page: int = 1, offset: int = 100
    ) -> List[NormalizedTransaction]:
        try:
            data = await self._request(
                module="account",
                action="txlist",
                address=address,
                startblock=0,
                endblock=99999999,
                page=page,
                offset=offset,
                sort="desc",
            )
            if data.get("status") == "0" and "No transactions found" in data.get("message", ""):
                return []
            if data.get("result") and isinstance(data["result"], str):
                logger.warning("Etherscan error for %s: %s", address, data["result"])
                return []
            return [self._parse_tx(tx) for tx in data.get("result", [])]
        except Exception as e:
            logger.error("Failed to fetch transactions for %s: %s", address, e)
            return []

    async def get_transactions_by_page(
        self, address: str, start_block: int, end_block: int, page: int = 1, offset: int = 100
    ) -> List[NormalizedTransaction]:
        try:
            data = await self._request(
                module="account",
                action="txlist",
                address=address,
                startblock=start_block,
                endblock=end_block,
                page=page,
                offset=offset,
                sort="desc",
            )
            if data.get("status") == "0" and "No transactions found" in data.get("message", ""):
                return []
            if data.get("result") and isinstance(data["result"], str):
                return []
            return [self._parse_tx(tx) for tx in data.get("result", [])]
        except Exception as e:
            logger.error("Failed to fetch transactions: %s", e)
            return []

    async def get_transaction_details(self, tx_hash: str) -> Optional[NormalizedTransaction]:
        try:
            data = await self._request(
                module="proxy",
                action="eth_getTransactionByHash",
                txhash=tx_hash,
            )
            raw = data.get("result")
            if not raw:
                return None

            value_wei = int(raw.get("value", "0"), 16)
            amount = value_wei / 1e18
            gas_price = int(raw.get("gasPrice", "0"), 16)

            return NormalizedTransaction(
                tx_hash=raw["hash"],
                sender_address=raw["from"].lower(),
                receiver_address=raw.get("to", "").lower() if raw.get("to") else "",
                blockchain="ethereum",
                amount=round(amount, 8),
                amount_usd=None,
                gas_fee=None,
                gas_fee_usd=None,
                token="ETH",
                block_number=int(raw.get("blockNumber", "0x0"), 16),
                timestamp=datetime.now(timezone.utc),
                status="confirmed",
            )
        except Exception as e:
            logger.error("Failed to fetch tx %s: %s", tx_hash, e)
            return None
