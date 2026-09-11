from app.blockchain.ethereum import EthereumAdapter
from app.config import settings

BSCSCAN_API_URL = "https://api.bscscan.com/api"


class BSCAdapter(EthereumAdapter):
    """BSC adapter — inherits from Ethereum (EVM-compatible) and overrides endpoints."""

    def __init__(self, api_key: str = ""):
        super().__init__(api_key=api_key or settings.BSCSCAN_API_KEY)
        self._base_url = BSCSCAN_API_URL

    @property
    def chain_name(self) -> str:
        return "bnb"

    @property
    def native_token(self) -> str:
        return "BNB"

    def _parse_tx(self, raw: dict):
        tx = super()._parse_tx(raw)
        tx.blockchain = "bnb"
        tx.token = "BNB"
        return tx
