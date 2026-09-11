from fastapi import FastAPI
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

@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.APP_NAME}
