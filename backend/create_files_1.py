import os

files_content = {
    "requirements.txt": """fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.36
asyncpg==0.29.0
alembic==1.13.3
python-jose[cryptography]==3.3.0
bcrypt==4.2.0
pydantic-settings==2.5.2
pydantic[email]==2.9.2
neo4j==5.25.0
reportlab==4.2.5
python-multipart==0.0.12
httpx==0.27.2
faker==30.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
aiofiles==24.1.0
""",
    ".env.example": """DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cryptoshield
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=cryptoshield123
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30
APP_NAME=CryptoShield AI
APP_VERSION=1.0.0
DEBUG=true
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
""",
    "app/__init__.py": """# CryptoShield AI Backend
""",
    "app/config.py": """from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cryptoshield"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "cryptoshield123"
    JWT_SECRET_KEY: str = "dev-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    APP_NAME: str = "CryptoShield AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
""",
    "app/database.py": """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    from app.models import user, wallet, transaction, wallet_feature, prediction, investigation, blacklist, notification, blockchain_config
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
""",
    "app/neo4j_client.py": """from neo4j import GraphDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self._driver = None
        self._connected = False

    def connect(self):
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            self._driver.verify_connectivity()
            self._connected = True
            logger.info("Neo4j connected successfully")
        except Exception as e:
            logger.warning(f"Neo4j connection failed (running in mock mode): {e}")
            self._connected = False

    def close(self):
        if self._driver:
            self._driver.close()

    @property
    def is_connected(self):
        return self._connected

    def run_query(self, query: str, parameters: dict = None):
        if not self._connected:
            return []
        with self._driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def create_wallet_node(self, address: str, blockchain: str, fraud_score: float = 0.0):
        if not self._connected:
            return None
        query = \"\"\"
        MERGE (w:Wallet {address: $address})
        SET w.blockchain = $blockchain, w.fraud_score = $fraud_score
        RETURN w
        \"\"\"
        return self.run_query(query, {"address": address, "blockchain": blockchain, "fraud_score": fraud_score})

    def create_transaction_edge(self, sender: str, receiver: str, tx_hash: str, amount: float, timestamp: str, blockchain: str):
        if not self._connected:
            return None
        query = \"\"\"
        MERGE (s:Wallet {address: $sender})
        MERGE (r:Wallet {address: $receiver})
        CREATE (s)-[:SENT {tx_hash: $tx_hash, amount: $amount, timestamp: $timestamp, blockchain: $blockchain}]->(r)
        \"\"\"
        return self.run_query(query, {"sender": sender, "receiver": receiver, "tx_hash": tx_hash, "amount": amount, "timestamp": timestamp, "blockchain": blockchain})

    def get_wallet_neighbors(self, address: str, hops: int = 2):
        if not self._connected:
            return {"nodes": [], "edges": []}
        query = \"\"\"
        MATCH path = (w:Wallet {address: $address})-[:SENT*1..2]-(neighbor:Wallet)
        RETURN path LIMIT 100
        \"\"\"
        return self.run_query(query, {"address": address})

    def get_graph_stats(self):
        if not self._connected:
            return {"nodes": 0, "edges": 0, "components": 0, "density": 0.0}
        node_count = self.run_query("MATCH (w:Wallet) RETURN count(w) as count")
        edge_count = self.run_query("MATCH ()-[r:SENT]->() RETURN count(r) as count")
        n = node_count[0]['count'] if node_count else 0
        e = edge_count[0]['count'] if edge_count else 0
        density = (2 * e) / (n * (n - 1)) if n > 1 else 0
        return {"nodes": n, "edges": e, "components": 1, "density": round(density, 6)}

neo4j_client = Neo4jClient()
""",
    "app/models/__init__.py": """from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.wallet_feature import WalletFeature
from app.models.prediction import Prediction, WalletCategory
from app.models.investigation import Investigation, InvestigationWallet, InvestigationNote
from app.models.blacklist import Blacklist
from app.models.notification import Notification
from app.models.blockchain_config import BlockchainConfig
""",
    "app/models/user.py": """from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    investigator = "investigator"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.investigator)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500))
    department = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
""",
    "app/models/wallet.py": """from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), unique=True, index=True, nullable=False)
    blockchain = Column(String(50), nullable=False)
    label = Column(String(255))
    tx_count = Column(Integer, default=0)
    balance = Column(Float, default=0.0)
    first_seen = Column(DateTime(timezone=True))
    last_active = Column(DateTime(timezone=True))
    is_blacklisted = Column(Boolean, default=False)
    fraud_score = Column(Float)
    risk_level = Column(String(20))
    category = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/models/transaction.py": """from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(255), unique=True, index=True, nullable=False)
    sender_address = Column(String(255), index=True, nullable=False)
    receiver_address = Column(String(255), index=True, nullable=False)
    blockchain = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    amount_usd = Column(Float)
    gas_fee = Column(Float)
    gas_fee_usd = Column(Float)
    token = Column(String(50), default="NATIVE")
    block_number = Column(BigInteger)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="confirmed")
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/models/wallet_feature.py": """from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class WalletFeature(Base):
    __tablename__ = "wallet_features"
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), index=True, nullable=False)
    blockchain = Column(String(50))
    incoming_tx = Column(Integer, default=0)
    outgoing_tx = Column(Integer, default=0)
    avg_tx_amount = Column(Float, default=0.0)
    max_tx_amount = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    active_days = Column(Integer, default=0)
    gas_usage = Column(Float, default=0.0)
    token_diversity = Column(Integer, default=1)
    neighbor_count = Column(Integer, default=0)
    degree_centrality = Column(Float, default=0.0)
    betweenness_centrality = Column(Float, default=0.0)
    pagerank = Column(Float, default=0.0)
    clustering_coefficient = Column(Float, default=0.0)
    cross_chain_tx_count = Column(Integer, default=0)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/models/prediction.py": """from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), index=True, nullable=False)
    fraud_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(50), default="mock-v1.0")
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WalletCategory(Base):
    __tablename__ = "wallet_categories"
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), index=True, nullable=False)
    category = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(50), default="mock-v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/models/investigation.py": """from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class InvestigationStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"
    archived = "archived"

class Investigation(Base):
    __tablename__ = "investigations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(InvestigationStatus), default=InvestigationStatus.open)
    priority = Column(String(20), default="medium")
    created_by_id = Column(Integer, index=True)
    assigned_to_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class InvestigationWallet(Base):
    __tablename__ = "investigation_wallets"
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), index=True)
    wallet_address = Column(String(255), nullable=False)
    blockchain = Column(String(50))
    added_at = Column(DateTime(timezone=True), server_default=func.now())

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/models/blacklist.py": """from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), index=True, nullable=False)
    blockchain = Column(String(50))
    category = Column(String(100))  # scam, mixer, exchange, darknet
    reason = Column(Text)
    source = Column(String(255))
    confidence = Column(String(20), default="high")
    is_active = Column(Boolean, default=True)
    added_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
""",
    "app/models/notification.py": """from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    metadata_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "app/models/blockchain_config.py": """from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.sql import func
from app.database import Base

class BlockchainConfig(Base):
    __tablename__ = "blockchain_configs"
    id = Column(Integer, primary_key=True, index=True)
    blockchain = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100))
    api_url = Column(String(500))
    api_key_encrypted = Column(String(500))
    is_enabled = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True))
    tx_count = Column(BigInteger, default=0)
    wallet_count = Column(Integer, default=0)
    block_height = Column(BigInteger, default=0)
    sync_status = Column(String(50), default="idle")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
""",
    "app/schemas/__init__.py": "",
    "app/schemas/auth.py": """from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    role: str = "investigator"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
""",
    "app/schemas/user.py": """from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    department: Optional[str]
    created_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    role: str = "investigator"
    department: Optional[str] = None
""",
    "app/schemas/wallet.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WalletResponse(BaseModel):
    id: int
    address: str
    blockchain: str
    label: Optional[str]
    tx_count: int
    balance: float
    first_seen: Optional[datetime]
    last_active: Optional[datetime]
    is_blacklisted: bool
    fraud_score: Optional[float]
    risk_level: Optional[str]
    category: Optional[str]

    class Config:
        from_attributes = True

class WalletCreate(BaseModel):
    address: str
    blockchain: str
    label: Optional[str] = None
""",
    "app/schemas/transaction.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionResponse(BaseModel):
    id: int
    tx_hash: str
    sender_address: str
    receiver_address: str
    blockchain: str
    amount: float
    amount_usd: Optional[float]
    gas_fee: Optional[float]
    token: str
    block_number: Optional[int]
    timestamp: datetime
    status: str
    is_flagged: bool

    class Config:
        from_attributes = True

class TransactionFilter(BaseModel):
    blockchain: Optional[str] = None
    status: Optional[str] = None
    token: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20
""",
    "app/schemas/prediction.py": """from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class FraudPredictionResponse(BaseModel):
    wallet_address: str
    fraud_score: float
    risk_level: str
    confidence: float
    last_activity: Optional[datetime]
    tx_count: int
    connected_wallets: int
    cross_chain_activity: bool
    prediction_time: datetime
    model_version: str

class WalletAttributionResponse(BaseModel):
    wallet_address: str
    category: str
    confidence: float
    secondary_categories: List[dict]
    prediction_time: datetime
    model_version: str

class ExplanationResponse(BaseModel):
    wallet_address: str
    top_features: List[dict]
    neighbor_influence: List[dict]
    important_transactions: List[dict]
    temporal_activity: List[dict]
    risk_factors: List[str]
    reasoning_text: str
    fraud_score: float
""",
    "app/schemas/investigation.py": """from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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

class InvestigationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    created_by_id: int
    assigned_to_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    content: str

class WalletAttach(BaseModel):
    wallet_address: str
    blockchain: str
""",
    "app/schemas/blacklist.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlacklistCreate(BaseModel):
    address: str
    blockchain: str
    category: str  # scam, mixer, exchange, darknet
    reason: Optional[str] = None
    source: Optional[str] = None
    confidence: str = "high"

class BlacklistUpdate(BaseModel):
    reason: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class BlacklistResponse(BaseModel):
    id: int
    address: str
    blockchain: str
    category: str
    reason: Optional[str]
    source: Optional[str]
    confidence: str
    is_active: bool
    added_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
""",
    "app/schemas/notification.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
""",
    "app/schemas/blockchain.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlockchainConfigUpdate(BaseModel):
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: Optional[bool] = None

class BlockchainConfigResponse(BaseModel):
    id: int
    blockchain: str
    display_name: str
    api_url: Optional[str]
    is_enabled: bool
    last_sync: Optional[datetime]
    tx_count: int
    wallet_count: int
    block_height: int
    sync_status: str

    class Config:
        from_attributes = True
""",
    "app/middleware/__init__.py": "",
    "app/middleware/auth.py": """from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select
from app.models.user import User

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except Exception:
        return None
""",
    "app/services/__init__.py": "",
    "app/services/auth_service.py": """from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "role": role, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    payload = {"email": email, "exp": expire, "type": "reset"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_reset_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "reset":
            return None
        return payload.get("email")
    except Exception:
        return None
""",
    "app/services/mock_data_service.py": """import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any

BLOCKCHAINS = ["bitcoin", "ethereum", "bnb", "polygon", "tron"]
WALLET_CATEGORIES = ["Exchange", "Mining Pool", "Scam Wallet", "Darknet Wallet", "Mixer", "Bridge", "DeFi Protocol", "NFT Marketplace", "Personal Wallet", "Unknown"]
RISK_LEVELS = ["low", "medium", "high", "critical"]
TOKENS = ["BTC", "ETH", "BNB", "MATIC", "TRX", "USDT", "USDC", "WETH", "LINK", "UNI"]

def generate_wallet_address(blockchain: str) -> str:
    prefix = {"bitcoin": "1", "ethereum": "0x", "bnb": "0x", "polygon": "0x", "tron": "T"}.get(blockchain, "0x")
    rand_hex = hashlib.sha256(str(random.random()).encode()).hexdigest()
    if prefix in ["0x"]:
        return f"0x{rand_hex[:40]}"
    elif prefix == "1":
        return f"1{rand_hex[:33]}"
    else:
        return f"T{rand_hex[:33]}"

def get_fraud_prediction(wallet_address: str) -> Dict[str, Any]:
    seed = sum(ord(c) for c in wallet_address)
    random.seed(seed)
    fraud_score = round(random.uniform(0.05, 0.98), 4)
    if fraud_score < 0.3:
        risk_level = "low"
    elif fraud_score < 0.6:
        risk_level = "medium"
    elif fraud_score < 0.8:
        risk_level = "high"
    else:
        risk_level = "critical"
    confidence = round(random.uniform(0.72, 0.98), 4)
    tx_count = random.randint(5, 5000)
    connected_wallets = random.randint(2, 200)
    last_activity = datetime.utcnow() - timedelta(days=random.randint(0, 365))
    random.seed()
    return {
        "wallet_address": wallet_address,
        "fraud_score": fraud_score,
        "risk_level": risk_level,
        "confidence": confidence,
        "last_activity": last_activity.isoformat(),
        "tx_count": tx_count,
        "connected_wallets": connected_wallets,
        "cross_chain_activity": random.random() > 0.5,
        "prediction_time": datetime.utcnow().isoformat(),
        "model_version": "mock-v1.0.0"
    }

def get_wallet_attribution(wallet_address: str) -> Dict[str, Any]:
    seed = sum(ord(c) for c in wallet_address) + 42
    random.seed(seed)
    primary_category = random.choice(WALLET_CATEGORIES)
    confidence = round(random.uniform(0.6, 0.97), 4)
    secondary = random.sample([c for c in WALLET_CATEGORIES if c != primary_category], k=2)
    secondary_categories = [{"category": cat, "confidence": round(random.uniform(0.05, 0.4), 3)} for cat in secondary]
    random.seed()
    return {
        "wallet_address": wallet_address,
        "category": primary_category,
        "confidence": confidence,
        "secondary_categories": secondary_categories,
        "prediction_time": datetime.utcnow().isoformat(),
        "model_version": "mock-v1.0.0"
    }

def get_wallet_explanation(wallet_address: str) -> Dict[str, Any]:
    seed = sum(ord(c) for c in wallet_address) + 99
    random.seed(seed)
    features = [
        {"name": "Degree Centrality", "importance": round(random.uniform(0.6, 0.95), 3), "value": round(random.uniform(0.01, 0.9), 3)},
        {"name": "Transaction Frequency", "importance": round(random.uniform(0.5, 0.9), 3), "value": random.randint(10, 5000)},
        {"name": "Average TX Amount", "importance": round(random.uniform(0.4, 0.85), 3), "value": round(random.uniform(0.001, 100), 4)},
        {"name": "Cross-Chain Activity", "importance": round(random.uniform(0.3, 0.8), 3), "value": random.randint(0, 50)},
        {"name": "Betweenness Centrality", "importance": round(random.uniform(0.2, 0.75), 3), "value": round(random.uniform(0, 0.5), 4)},
        {"name": "Clustering Coefficient", "importance": round(random.uniform(0.2, 0.7), 3), "value": round(random.uniform(0, 1), 4)},
        {"name": "Token Diversity", "importance": round(random.uniform(0.15, 0.65), 3), "value": random.randint(1, 20)},
        {"name": "PageRank Score", "importance": round(random.uniform(0.1, 0.6), 3), "value": round(random.uniform(0, 0.01), 6)},
    ]
    features.sort(key=lambda x: x["importance"], reverse=True)
    risk_factors_pool = [
        "Connected to multiple blacklisted wallets",
        "High transaction frequency anomaly detected",
        "Cross-chain movement pattern matches mixer behavior",
        "Abnormal transfer amounts (round numbers)",
        "Interaction with known malicious smart contracts",
        "Funds received from flagged exchange withdrawal",
        "Rapid layering of transactions detected",
        "Low time-delta between incoming and outgoing transfers",
    ]
    risk_factors = random.sample(risk_factors_pool, k=random.randint(2, 5))
    neighbor_influence = []
    for i in range(3):
        addr = generate_wallet_address("ethereum")
        neighbor_influence.append({"address": addr, "influence_score": round(random.uniform(0.1, 0.9), 3), "is_blacklisted": random.random() > 0.6})
    temporal_activity = []
    base_date = datetime.utcnow() - timedelta(days=30)
    for day in range(30):
        date = base_date + timedelta(days=day)
        temporal_activity.append({"date": date.strftime("%Y-%m-%d"), "tx_count": random.randint(0, 50), "volume": round(random.uniform(0, 100), 4)})
    important_txs = []
    for i in range(3):
        important_txs.append({
            "tx_hash": f"0x{hashlib.md5(str(random.random()).encode()).hexdigest()}",
            "amount": round(random.uniform(0.1, 1000), 4),
            "blockchain": random.choice(BLOCKCHAINS),
            "importance": round(random.uniform(0.5, 1.0), 3),
            "timestamp": (datetime.utcnow() - timedelta(days=random.randint(1, 60))).isoformat()
        })
    fraud_score = get_fraud_prediction(wallet_address)["fraud_score"]
    reasoning_parts = []
    if fraud_score > 0.7:
        reasoning_parts.append(f"This wallet exhibits HIGH-RISK behavior with a fraud score of {fraud_score:.1%}.")
    elif fraud_score > 0.4:
        reasoning_parts.append(f"This wallet shows MODERATE-RISK indicators with a fraud score of {fraud_score:.1%}.")
    else:
        reasoning_parts.append(f"This wallet appears LOW-RISK with a fraud score of {fraud_score:.1%}.")
    reasoning_parts.append(f"Key contributing factors include: {', '.join(risk_factors[:2])}.")
    reasoning_parts.append(f"The GNN model analyzed {len(features)} temporal graph features and {len(neighbor_influence)} neighbor wallets to arrive at this conclusion.")
    random.seed()
    return {
        "wallet_address": wallet_address,
        "top_features": features,
        "neighbor_influence": neighbor_influence,
        "important_transactions": important_txs,
        "temporal_activity": temporal_activity,
        "risk_factors": risk_factors,
        "reasoning_text": " ".join(reasoning_parts),
        "fraud_score": fraud_score
    }

def generate_mock_transactions(count: int = 50, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    transactions = []
    base_time = datetime.utcnow()
    for i in range(count):
        blockchain = random.choice(BLOCKCHAINS)
        tx_hash = f"0x{hashlib.sha256(str(i + random.random()).encode()).hexdigest()[:64]}"
        amount = round(random.uniform(0.001, 10000), 6)
        transactions.append({
            "id": i + 1,
            "tx_hash": tx_hash,
            "sender_address": generate_wallet_address(blockchain),
            "receiver_address": generate_wallet_address(blockchain),
            "blockchain": blockchain,
            "amount": amount,
            "amount_usd": round(amount * random.uniform(100, 50000), 2),
            "gas_fee": round(random.uniform(0.00001, 0.01), 8),
            "token": random.choice(TOKENS),
            "block_number": random.randint(1000000, 50000000),
            "timestamp": (base_time - timedelta(hours=random.randint(0, 8760))).isoformat(),
            "status": random.choice(["confirmed", "confirmed", "confirmed", "pending", "failed"]),
            "is_flagged": random.random() > 0.85
        })
    total = count
    start = (page - 1) * page_size
    end = start + page_size
    return {"items": transactions[start:end], "total": total, "page": page, "page_size": page_size, "pages": (total + page_size - 1) // page_size}

def generate_mock_wallets(count: int = 30) -> List[Dict[str, Any]]:
    wallets = []
    for i in range(count):
        blockchain = random.choice(BLOCKCHAINS)
        address = generate_wallet_address(blockchain)
        fraud_score = round(random.uniform(0, 1), 4)
        risk_level = "low" if fraud_score < 0.3 else "medium" if fraud_score < 0.6 else "high" if fraud_score < 0.8 else "critical"
        wallets.append({
            "id": i + 1,
            "address": address,
            "blockchain": blockchain,
            "tx_count": random.randint(1, 10000),
            "balance": round(random.uniform(0, 1000), 6),
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "category": random.choice(WALLET_CATEGORIES),
            "is_blacklisted": random.random() > 0.9,
            "last_active": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat()
        })
    return wallets

def generate_dashboard_stats() -> Dict[str, Any]:
    base = datetime.utcnow()
    fraud_trend = []
    for i in range(30):
        date = base - timedelta(days=29 - i)
        fraud_trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "flagged": random.randint(5, 80),
            "total": random.randint(200, 2000),
            "score_avg": round(random.uniform(0.2, 0.6), 3)
        })
    volume_trend = []
    for i in range(14):
        date = base - timedelta(days=13 - i)
        volume_trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "bitcoin": round(random.uniform(1000, 50000), 2),
            "ethereum": round(random.uniform(500, 30000), 2),
            "bnb": round(random.uniform(200, 10000), 2),
            "polygon": round(random.uniform(100, 5000), 2),
            "tron": round(random.uniform(50, 3000), 2)
        })
    return {
        "total_wallets": random.randint(45000, 80000),
        "fraudulent_wallets": random.randint(1200, 3500),
        "total_transactions": random.randint(500000, 2000000),
        "blockchain_networks": 5,
        "active_investigations": random.randint(12, 45),
        "avg_fraud_score": round(random.uniform(0.2, 0.45), 3),
        "fraud_trend": fraud_trend,
        "volume_trend": volume_trend,
        "blockchain_distribution": [
            {"name": "Bitcoin", "value": random.randint(20, 35)},
            {"name": "Ethereum", "value": random.randint(25, 40)},
            {"name": "BNB Chain", "value": random.randint(10, 20)},
            {"name": "Polygon", "value": random.randint(8, 15)},
            {"name": "Tron", "value": random.randint(5, 12)}
        ],
        "wallet_category_distribution": [
            {"name": cat, "value": random.randint(50, 500)}
            for cat in WALLET_CATEGORIES
        ],
        "top_suspicious_wallets": generate_mock_wallets(5)
    }
""",
    "app/utils/__init__.py": "",
    "app/utils/pdf_generator.py": """from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

def generate_investigation_report(wallet_data: dict, fraud_data: dict, explanation_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)
    header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0f3460'), spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=4)
    story = []
    # Title
    story.append(Paragraph("CryptoShield AI", title_style))
    story.append(Paragraph("Cryptocurrency Fraud Investigation Report", styles['Heading2']))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0f3460')))
    story.append(Spacer(1, 0.2*inch))
    # Wallet Summary
    story.append(Paragraph("Wallet Summary", header_style))
    wallet_table_data = [
        ["Field", "Value"],
        ["Address", wallet_data.get("address", "N/A")],
        ["Blockchain", wallet_data.get("blockchain", "N/A")],
        ["Category", wallet_data.get("category", "Unknown")],
        ["Transaction Count", str(wallet_data.get("tx_count", 0))],
        ["Balance", f"{wallet_data.get('balance', 0):.6f}"],
        ["Last Active", str(wallet_data.get("last_active", "N/A"))],
    ]
    t = Table(wallet_table_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4ff')]),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    # Fraud Score
    story.append(Paragraph("Fraud Risk Assessment", header_style))
    fraud_score = fraud_data.get("fraud_score", 0)
    risk_level = fraud_data.get("risk_level", "unknown")
    confidence = fraud_data.get("confidence", 0)
    fraud_color = colors.green if fraud_score < 0.3 else colors.orange if fraud_score < 0.6 else colors.red
    risk_table_data = [
        ["Metric", "Value"],
        ["Fraud Score", f"{fraud_score:.1%}"],
        ["Risk Level", risk_level.upper()],
        ["Confidence", f"{confidence:.1%}"],
        ["Connected Wallets", str(fraud_data.get("connected_wallets", 0))],
        ["Cross-Chain Activity", "Yes" if fraud_data.get("cross_chain_activity") else "No"],
        ["Model Version", fraud_data.get("model_version", "N/A")],
    ]
    t2 = Table(risk_table_data, colWidths=[2*inch, 4*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4ff')]),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (1, 2), (1, 2), fraud_color),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.2*inch))
    # Risk Factors
    risk_factors = explanation_data.get("risk_factors", [])
    if risk_factors:
        story.append(Paragraph("Risk Factors Identified", header_style))
        for factor in risk_factors:
            story.append(Paragraph(f"• {factor}", body_style))
        story.append(Spacer(1, 0.1*inch))
    # AI Reasoning
    reasoning = explanation_data.get("reasoning_text", "")
    if reasoning:
        story.append(Paragraph("AI Model Reasoning", header_style))
        story.append(Paragraph(reasoning, body_style))
        story.append(Spacer(1, 0.1*inch))
    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Paragraph("This report was generated by CryptoShield AI. For investigative purposes only.", 
                            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
""",
    "app/utils/csv_handler.py": """import csv
import io
from typing import List, Dict, Any

def generate_csv(data: List[Dict[str, Any]], fieldnames: List[str] = None) -> bytes:
    if not data:
        return b""
    if not fieldnames:
        fieldnames = list(data[0].keys())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(data)
    return buffer.getvalue().encode('utf-8')

def parse_csv(content: bytes) -> List[Dict[str, Any]]:
    buffer = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(buffer)
    return [row for row in reader]
""",
    "app/utils/helpers.py": """from datetime import datetime

def format_datetime(dt: datetime) -> str:
    return dt.isoformat() if dt else None
"""
}

for filepath, content in files_content.items():
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(os.path.join(r"e:\final project\backend", dirname), exist_ok=True)
    with open(os.path.join(r"e:\final project\backend", filepath), 'w', encoding='utf-8') as f:
        f.write(content)
print("Files created successfully.")
