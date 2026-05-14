# Bank Anomaly Detection Engine

Autonomous real-time reconciliation and fraud detection across banking data streams.

[![Render](https://img.shields.io/badge/Backend-Render-46E3B7)](https://render.com) [![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000)](https://vercel.com) [![Python](https://img.shields.io/badge/Python-3.11-3776AB)](https://python.org) [![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev)

> Built for DualEntry portfolio demonstration. 100% free tier.

## Live Demo

- **Backend API**: https://bank-anomaly-api.onrender.com/api/v1/health
- **Frontend Dashboard**: https://bank-anomaly-dashboard.vercel.app
- **Demo Video**: [90-second walkthrough](https://loom.com/share/your-link-here)

> Note: Hosted on Render's free tier. The server may take 30 seconds to wake up after inactivity. Please wait for the initial load.

## Architecture

```
Plaid Sandbox → Ingestion → SQLite → Feature Engineering
                                ↓
                    Anomaly Detector (Dual-Layer)
                    ├─ Statistical: Rolling Z-Score
                    └─ ML: Isolation Forest
                                ↓
                    LLM Explainer (NVIDIA NIM)
                                ↓
                    FastAPI REST API ←→ React Dashboard
```

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Data Source | Plaid API Sandbox | Realistic synthetic data, $0 cost |
| Backend | Python 3.11, FastAPI | Async-native, auto OpenAPI docs |
| ML | Scikit-Learn (Isolation Forest + Z-Score) | Unsupervised, no labels needed |
| LLM | NVIDIA NIM (dracarys-llama-3.1-70b-instruct) | Free endpoint, validated output |
| Database | SQLite | Zero config, survives on Render disk |
| Frontend | React 18, TailwindCSS | Component-based, utility-first CSS |
| Charts | Recharts | Declarative, composable charting |
| Design | Google Stitch MCP | AI-generated components, rapid iteration |
| Deployment | Render + Vercel | Free tier, Git-based deploys |

## Features

- **Autonomous Ingestion**: Polls Plaid Sandbox every 2 minutes
- **Dual-Layer Detection**: Statistical (Z-Score) + ML (Isolation Forest)
- **AI Explanations**: NVIDIA LLM generates one-sentence anomaly descriptions
- **Real-Time Dashboard**: 5-second polling with live updates
- **Vendor Drill-Down**: 6-month trend charts with anomaly highlighting
- **Graceful Degradation**: Fallback templates if LLM API is unavailable

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Plaid Sandbox account (free)
- NVIDIA NIM account (free)

### Backend

```bash
cd backend
cp .env.example .env
# Fill in: PLAID_CLIENT_ID, PLAID_SECRET, NVIDIA_NIM_API_KEY

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API will be available at `http://localhost:8000/api/v1`

### Frontend

```bash
cd frontend
cp .env.example .env
# Set: VITE_API_URL=http://localhost:8000/api/v1

npm install
npm run dev
```

Dashboard will be available at `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/transactions` | List transactions (paginated) |
| GET | `/api/v1/anomalies` | List anomalies with explanations |
| POST | `/api/v1/detect` | Trigger detection pipeline |
| GET | `/api/v1/stats` | Dashboard KPIs |

## Design

UI components generated with [Google Stitch MCP](https://stitch.withgoogle.com/) for rapid, production-grade design-to-code workflow.

## Interview Notes

### Why Isolation Forest?

Unsupervised learning requires no labeled fraud data. It learns "normal" patterns and isolates outliers — perfect for detecting unknown anomaly types.

### Why Dual-Layer Detection?

Statistical layer (Z-Score) provides interpretable, threshold-based flags for clear deviations. ML layer (Isolation Forest) catches subtle structural patterns that statistics miss.

### Why NVIDIA NIM Free Tier?

Zero cost with validated output quality. The dracarys-llama-3.1-70b-instruct model generates concise, factual explanations averaging 19 words per response.

### Why SQLite?

Sufficient for 1k–5k demo rows. Zero configuration, sub-millisecond queries, survives on Render persistent disk. Upgrade path to PostgreSQL documented.

### Why Stitch MCP?

AI-native design-to-code workflow that generates production Tailwind components in seconds. Demonstrates modern engineering velocity with AI tooling.

## Project Structure

```
backend/
├── config.py              # Pydantic settings
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── render.yaml            # Render deploy config
├── database/
│   └── models.py          # SQLAlchemy models
├── ingestion/
│   ├── plaid_client.py    # Plaid API wrapper
│   └── pipeline.py        # APScheduler ingestion
├── features/
│   └── engineer.py        # Rolling stats computation
├── detection/
│   ├── statistical.py     # Z-Score detector
│   ├── isolation_forest.py # ML detector
│   ├── duplicate.py       # Duplicate detector
│   └── orchestrator.py    # Detection coordinator
└── llm/
    ├── nvidia_nim.py      # NVIDIA NIM client
    ├── fallback.py        # Rule-based fallback
    └── explainer.py       # Explanation orchestrator

frontend/
├── src/
│   ├── App.jsx            # Main application
│   ├── main.jsx           # React entry point
│   ├── index.css          # Global styles
│   ├── hooks/
│   │   └── useInterval.js # Polling hook
│   ├── services/
│   │   └── api.js         # Axios client
│   └── components/        # Stitch-generated components
│       ├── Layout.jsx
│       ├── StatsBar.jsx
│       ├── TransactionFeed.jsx
│       ├── AnomalyCard.jsx
│       └── TrendModal.jsx
├── tailwind.config.js     # Design tokens
├── vite.config.js         # Vite config
├── vercel.json            # Vercel deploy config
└── package.json           # NPM dependencies
```

## Deployment

### Backend (Render)

1. Push backend code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set environment variables in Render dashboard
5. Add 1GB disk mounted at `/data`
6. Deploy

### Frontend (Vercel)

1. Push frontend code to GitHub
2. Import project on Vercel
3. Set environment variable: `VITE_API_URL=https://your-render-url.onrender.com/api/v1`
4. Deploy

## License

MIT
