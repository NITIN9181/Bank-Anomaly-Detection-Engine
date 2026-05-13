# Bank Anomaly Detection Engine

Autonomous real-time reconciliation and fraud detection across banking data streams.

Built for DualEntry portfolio demonstration.

---

## Architecture

```
Plaid Sandbox -> [Ingestion Service] -> SQLite (transactions)
                                           |
                                    [Feature Engineer]
                                           |
                                    SQLite (vendor_profiles)
                                           |
                                    [Anomaly Detector]
                                           |
                                    SQLite (anomalies)
                                           |
                                    [LLM Explainer]
                                           |
                                    SQLite (anomalies.explanation updated)
                                           |
                                    [FastAPI] <--- [React Dashboard]
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Source | Plaid API Sandbox |
| Backend | Python 3.11, FastAPI, Uvicorn |
| ML | Scikit-Learn (Isolation Forest, Rolling Z-Score) |
| LLM | NVIDIA NIM (dracarys-llama-3.1-70b-instruct) |
| Database | SQLite |
| Frontend | React 18, TailwindCSS, Recharts |
| Design | Google Stitch MCP (AI design-to-code) |
| Deployment | Render (backend), Vercel (frontend) |

---

## Live Demo

- **Backend**: https://bank-anomaly-api.onrender.com
- **Frontend**: https://bank-anomaly-dashboard.vercel.app
- **Demo Video**: [90-second walkthrough](link-to-loom)

> **Note**: Hosted on Render free tier. The server may take 30 seconds to wake up after inactivity.

---

## Local Setup

### Backend

```bash
cd backend
cp .env.example .env
# Fill in PLAID_CLIENT_ID, PLAID_SECRET, NVIDIA_NIM_API_KEY

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend

```bash
cd frontend
cp .env.example .env
# Set REACT_APP_API_URL=http://localhost:8000/api/v1

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/transactions` | List transactions (paginated) |
| GET | `/api/v1/anomalies` | List anomalies (paginated) |
| POST | `/api/v1/detect` | Trigger anomaly detection |
| GET | `/api/v1/stats` | Dashboard statistics |

### Example: Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2026-05-13T10:30:00Z",
  "version": "1.0.0"
}
```

### Example: List Transactions

```bash
curl "http://localhost:8000/api/v1/transactions?limit=10&offset=0"
```

Response:
```json
{
  "items": [
    {
      "id": 1,
      "plaid_transaction_id": "txn_abc123",
      "amount": 5000.00,
      "date": "2026-05-10",
      "merchant_name": "AWS",
      "category": "Software",
      "created_at": "2026-05-12T10:00:00Z"
    }
  ],
  "total": 1240,
  "limit": 10,
  "offset": 0
}
```

---

## Environment Variables

### Backend (`.env`)

```bash
# Plaid Configuration
PLAID_CLIENT_ID=your_plaid_client_id_here
PLAID_SECRET=your_plaid_sandbox_secret_here
PLAID_ENV=sandbox

# NVIDIA NIM Configuration
NVIDIA_NIM_API_KEY=nvapi-your_nvidia_key_here

# Database Configuration
DATABASE_PATH=./anomalies.db

# Application Environment
ENVIRONMENT=development
```

### Frontend (`.env`)

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## Design

UI components generated with [Google Stitch MCP](https://stitch.withgoogle.com/) for rapid, production-grade design-to-code workflow.

---

## Interview Notes

### Why Isolation Forest?

Unsupervised learning requires no labeled fraud data. It learns "normal" patterns and isolates outliers — perfect for unknown anomaly types.

### Why Dual-Layer Detection?

Statistical layer (Z-Score) provides interpretable, rule-based flags for clear deviations. ML layer (Isolation Forest) catches subtle structural patterns humans miss.

### Why NVIDIA NIM Free Tier?

Zero cost with validated output quality. The dracarys-llama-3.1-70b-instruct model generates concise, factual explanations at ~19 words per response.

### Why SQLite?

Sufficient for 1k-5k demo rows. Zero config, zero network latency, survives on Render persistent disk. Upgrade path to PostgreSQL documented.

### Why Stitch MCP?

AI-native design-to-code workflow that generates production Tailwind components in seconds. Demonstrates modern engineering velocity with AI tooling.

---

## Project Status

**Phase 1: Foundation** ✅ Complete
- Backend scaffold with FastAPI
- SQLite database schema
- Plaid API integration
- Transaction ingestion pipeline
- Vendor profile feature engineering

**Phase 2: Intelligence** 🚧 In Progress
- Anomaly detection (Statistical + ML)
- NVIDIA NIM LLM integration
- Explanation generation

**Phase 3: Presentation** ⏳ Planned
- React dashboard
- Real-time polling
- Vendor trend charts

**Phase 4: Deployment** ⏳ Planned
- Render backend deployment
- Vercel frontend deployment
- Production configuration

---

## License

MIT
