# CryptoShield AI 🛡️

**Advanced Cryptocurrency Fraud Detection & Wallet Attribution Platform**

Powered by a Temporal Explainable Multi-Chain Graph Neural Network.

---

## ✨ Features

1. 🔍 **Fraud Detection** — Analyze wallet behavior and score fraud risk 0–100%
2. 🏷️ **Wallet Attribution** — Classify wallets (Exchange, Mixer, Scam, DeFi, etc.)
3. 🧠 **Explainable AI** — GNN feature importance, temporal activity, risk reasoning
4. 📊 **Analytics Dashboard** — Real-time fraud trends, volume charts, distributions
5. 🕸️ **Graph Visualization** — Interactive Cytoscape.js transaction network
6. ⛓️ **Multi-Chain** — Bitcoin, Ethereum, BNB Chain, Polygon, Tron
7. 🗂️ **Investigation Module** — Case management, notes, PDF reports
8. 🚫 **Blacklist Management** — CRUD for scam wallets, mixers, exchanges
9. 🔔 **Notifications** — Real-time alerts for fraud detection events
10. 👥 **Role-Based Access** — Admin and Investigator roles with JWT auth

---

## 🚀 Quick Start

### Option A: Docker Compose (Recommended)

```bash
# Clone and start all services
docker-compose up --build
```

Then open:
1. **Frontend**: http://localhost:5173
2. **Backend API**: http://localhost:8000
3. **Swagger Docs**: http://localhost:8000/docs
4. **Neo4j Browser**: http://localhost:7474

### Option B: Local Development

#### Prerequisites
1. Python 3.11+
2. Node.js 20+
3. PostgreSQL 16 (or use Docker for DB only)
4. Neo4j 5.x (optional — falls back to mock mode)

#### Start Databases Only (Docker)
```bash
docker-compose up postgres neo4j -d
```

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env if needed

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Optional: Seed demo data
python seed_data.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Administrator | admin@cryptoshield.ai | admin123 |
| Investigator | investigator@cryptoshield.ai | investigator123 |

---

## 📁 Project Structure

```
cryptoshield-ai/
├── frontend/          # React + Tailwind CSS frontend
│   └── src/
│       ├── pages/     # All 16 app pages
│       ├── components/# Reusable UI components
│       ├── context/   # Auth + Notification contexts
│       ├── services/  # API layer (axios)
│       └── utils/     # Formatters, constants
│
├── backend/           # FastAPI backend
│   └── app/
│       ├── models/    # SQLAlchemy ORM models
│       ├── schemas/   # Pydantic schemas
│       ├── routers/   # 16 API routers
│       ├── services/  # Business logic + mock data
│       └── utils/     # PDF generator, CSV handler
│
└── docker-compose.yml # All 4 services
```

---

## 🔌 API Documentation

Swagger UI is auto-generated at: **http://localhost:8000/docs**

### Key Endpoints

| Module | Endpoint | Description |
|--------|----------|-------------|
| Auth | `POST /api/auth/login` | JWT login |
| Fraud | `POST /api/fraud/predict` | Fraud score for wallet |
| Attribution | `POST /api/attribution/predict` | Wallet category |
| Explainability | `POST /api/explainability/explain` | Full AI explanation |
| Graph | `GET /api/graph/wallet/{address}` | Transaction network |
| AI Model | `GET /api/ai/model-status` | Model info |
| AI Model | `POST /api/ai/train-model` | Trigger training |

---

## 🤖 AI Model Integration

The system is designed for seamless AI model replacement. Mock endpoints currently return realistic randomized responses.

To connect the real Temporal GNN:

1. Replace the mock functions in `backend/app/services/mock_data_service.py`
2. Or implement real logic in `backend/app/routers/ai_model.py`
3. No frontend changes required — all responses use the same JSON schema

### Expected AI Pipeline
```
Blockchain APIs
    ↓
Transaction Collection (PostgreSQL)
    ↓
Graph Construction (Neo4j)
    ↓
Temporal Graph Creation
    ↓
Feature Engineering
    ↓
Temporal GNN (PyTorch Geometric)
    ↓
Fraud Detection + Wallet Attribution
    ↓
Explainable AI (GNNExplainer / GraphSHAP)
    ↓
Prediction REST API → Dashboard
```

---

## 🗄️ Database Schema

### PostgreSQL Tables
1. `users` — Authentication and roles
2. `wallets` — Wallet metadata and risk scores
3. `transactions` — Transaction records (multi-chain)
4. `wallet_features` — Engineered graph features
5. `predictions` — Fraud prediction history
6. `wallet_categories` — Attribution predictions
7. `investigations` — Case management
8. `investigation_wallets` — Case-wallet relationships
9. `investigation_notes` — Case notes
10. `blacklist` — Blacklisted wallets
11. `notifications` — User notifications
12. `blockchain_configs` — API configurations

### Neo4j Graph
```cypher
(:Wallet {address, blockchain, fraud_score, risk_level})
-[:SENT {tx_hash, amount, timestamp, blockchain}]->
(:Wallet)
```

---

## 🛠️ Environment Variables

See `backend/.env.example` for all available settings.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection |
| `JWT_SECRET_KEY` | (required) | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 24 hours |
| `DEBUG` | `true` | Enable debug logging |

---

## 📄 License

MIT License — for academic and research purposes.

---

*CryptoShield AI — Protecting the blockchain ecosystem with AI-powered intelligence.*
