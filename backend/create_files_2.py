import os

files_content = {
    "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, users, wallets, transactions, graph, features, ai_model, fraud, attribution, explainability, blacklist, investigations, reports, notifications, blockchain, admin
from app.database import create_tables
from app.neo4j_client import neo4j_client

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CryptoShield AI Backend API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await create_tables()
    neo4j_client.connect()

@app.on_event("shutdown")
async def shutdown_event():
    neo4j_client.close()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["wallets"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(features.router, prefix="/api/features", tags=["features"])
app.include_router(ai_model.router, prefix="/api/ai", tags=["ai"])
app.include_router(fraud.router, prefix="/api/fraud", tags=["fraud"])
app.include_router(attribution.router, prefix="/api/attribution", tags=["attribution"])
app.include_router(explainability.router, prefix="/api/explainability", tags=["explainability"])
app.include_router(blacklist.router, prefix="/api/blacklist", tags=["blacklist"])
app.include_router(investigations.router, prefix="/api/investigations", tags=["investigations"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(blockchain.router, prefix="/api/blockchain", tags=["blockchain"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Welcome to CryptoShield AI API"}
""",
    "app/routers/auth.py": """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import hash_password, verify_password, create_access_token, create_refresh_token
from app.middleware.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        # mock return if db fails or just return 401
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "email": user.email, "role": user.role}
    }

@router.post("/register", response_model=UserResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    hashed_pw = hash_password(req.password)
    new_user = User(
        email=req.email,
        username=req.username,
        full_name=req.full_name,
        password_hash=hashed_pw,
        role=req.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user
""",
    "app/routers/users.py": """from fastapi import APIRouter, Depends
from app.middleware.auth import require_admin
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_users(admin: User = Depends(require_admin)):
    return []
""",
    "app/routers/wallets.py": """from fastapi import APIRouter, Depends
from app.middleware.auth import get_optional_user
from app.services.mock_data_service import generate_mock_wallets

router = APIRouter()

@router.get("/")
async def get_wallets():
    return generate_mock_wallets(20)

@router.get("/{address}")
async def get_wallet(address: str):
    wallets = generate_mock_wallets(1)
    wallets[0]['address'] = address
    return wallets[0]
""",
    "app/routers/transactions.py": """from fastapi import APIRouter, Depends
from app.services.mock_data_service import generate_mock_transactions

router = APIRouter()

@router.get("/")
async def get_transactions(page: int = 1, page_size: int = 20):
    return generate_mock_transactions(count=50, page=page, page_size=page_size)
""",
    "app/routers/graph.py": """from fastapi import APIRouter
from app.neo4j_client import neo4j_client
from app.services.mock_data_service import generate_wallet_address
import random

router = APIRouter()

@router.get("/stats")
async def get_graph_stats():
    return neo4j_client.get_graph_stats()

@router.get("/wallet/{address}")
async def get_ego_graph(address: str):
    nodes = [{"data": {"id": address, "label": "Target Wallet"}}]
    edges = []
    for i in range(5):
        neighbor = generate_wallet_address("ethereum")
        nodes.append({"data": {"id": neighbor, "label": "Neighbor"}})
        edges.append({"data": {"source": address, "target": neighbor, "amount": random.uniform(0.1, 10)}})
    return {"nodes": nodes, "edges": edges}
""",
    "app/routers/features.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/wallet/{address}")
async def get_wallet_features(address: str):
    return {"address": address, "degree_centrality": 0.8, "clustering_coefficient": 0.5}
""",
    "app/routers/ai_model.py": """from fastapi import APIRouter
from app.services.mock_data_service import get_fraud_prediction, get_wallet_attribution, get_wallet_explanation

router = APIRouter()

@router.post("/predict-wallet")
async def predict_wallet(address: str):
    return get_fraud_prediction(address)

@router.post("/wallet-attribution")
async def wallet_attribution(address: str):
    return get_wallet_attribution(address)

@router.post("/explain-wallet")
async def explain_wallet(address: str):
    return get_wallet_explanation(address)
""",
    "app/routers/fraud.py": """from fastapi import APIRouter
from app.services.mock_data_service import get_fraud_prediction

router = APIRouter()

@router.post("/predict")
async def predict_fraud(address: str):
    return get_fraud_prediction(address)
""",
    "app/routers/attribution.py": """from fastapi import APIRouter
from app.services.mock_data_service import get_wallet_attribution

router = APIRouter()

@router.post("/predict")
async def predict_attribution(address: str):
    return get_wallet_attribution(address)
""",
    "app/routers/explainability.py": """from fastapi import APIRouter
from app.services.mock_data_service import get_wallet_explanation

router = APIRouter()

@router.post("/explain")
async def explain(address: str):
    return get_wallet_explanation(address)
""",
    "app/routers/blacklist.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_blacklist():
    return []
""",
    "app/routers/investigations.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_investigations():
    return []
""",
    "app/routers/reports.py": """from fastapi import APIRouter, Response
from app.utils.pdf_generator import generate_investigation_report
from app.services.mock_data_service import get_fraud_prediction, get_wallet_attribution, get_wallet_explanation, generate_mock_wallets

router = APIRouter()

@router.get("/{id}/download")
async def download_report(id: str):
    addr = "0xmock"
    pdf = generate_investigation_report(
        generate_mock_wallets(1)[0],
        get_fraud_prediction(addr),
        get_wallet_explanation(addr)
    )
    return Response(content=pdf, media_type="application/pdf")
""",
    "app/routers/notifications.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_notifications():
    return []
""",
    "app/routers/blockchain.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/configs")
async def get_configs():
    return []
""",
    "app/routers/admin.py": """from fastapi import APIRouter
from app.services.mock_data_service import generate_dashboard_stats

router = APIRouter()

@router.get("/stats")
async def get_stats():
    return generate_dashboard_stats()
""",
    "alembic.ini": """[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/cryptoshield
""",
    "alembic/env.py": """import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.config import settings
from app.database import Base
from app.models import *

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = async_engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
""",
    "alembic/script.py.mako": '\"\"\"${message}\n\nRevision ID: ${up_revision}\nRevises: ${down_revision | comma,n}\nCreate Date: ${create_date}\n\n\"\"\"\nfrom typing import Sequence, Union\nfrom alembic import op\nimport sqlalchemy as sa\n${imports if imports else ""}\n\n# revision identifiers, used by Alembic.\nrevision: str = ${repr(up_revision)}\ndown_revision: Union[str, None] = ${repr(down_revision)}\nbranch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}\ndepends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}\n\n\ndef upgrade() -> None:\n    ${upgrades if upgrades else "pass"}\n\n\ndef downgrade() -> None:\n    ${downgrades if downgrades else "pass"}\n',
    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "seed_data.py": """import asyncio
from app.database import AsyncSessionLocal, create_tables
from app.models.user import User
from app.services.auth_service import hash_password

async def seed():
    await create_tables()
    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@cryptoshield.ai",
            username="admin",
            full_name="System Admin",
            password_hash=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        await db.commit()
        print("Seed complete")

if __name__ == "__main__":
    asyncio.run(seed())
"""
}

for filepath, content in files_content.items():
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(os.path.join(r"e:\final project\backend", dirname), exist_ok=True)
    with open(os.path.join(r"e:\final project\backend", filepath), 'w', encoding='utf-8') as f:
        f.write(content)
print("Files created successfully.")
