# Bank Anomaly Detection Engine

> An autonomous, real-time fraud detection system for banking transactions — built for fraud analysts and risk teams who need flagged anomalies explained in plain English.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?logo=scikitlearn&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Live demo:** [bank-anomaly-detection-engine.vercel.app](https://bank-anomaly-detection-engine.vercel.app/)
**API base:** [bank-anomaly-engine-latest.onrender.com/api/v1](https://bank-anomaly-engine-latest.onrender.com/api/v1)

---

## About the Project

Banks process thousands of transactions daily, and manually reviewing each one for fraud is impractical. The Bank Anomaly Detection Engine ingests banking transactions from the Plaid Sandbox API, runs them through a multi-layer detection pipeline, and produces human-readable explanations for every flagged anomaly — so an analyst can understand *why* a transaction looks suspicious, not just *that* it does.

What makes this approach different is the combination of **unsupervised ML** (no labeled fraud data required) with a **transparent statistical layer** and an **explainability engine**. Detection works on day one without a training corpus of confirmed fraud, and every flag comes with a confidence score, a feature-contribution breakdown, recommended actions, and an interactive "what-if" simulator. When the LLM explanation service is unavailable, the system falls back to deterministic rule-based templates, so explanations are always present.

<!-- Replace with an actual screenshot or demo GIF placed in ./assets/ -->
![Demo](./assets/demo.png)

---

## Features

- **Dual-layer ML detection** — combines a statistical Z-Score detector (deviation > 3.0 from a vendor's 6-month baseline) with an unsupervised Isolation Forest model (anomaly score < -0.15).
- **Duplicate charge detection** — flags transactions with the same merchant, amount, and date within a 24-hour window.
- **Cross-account fraud ring detection** — identifies coordinated spending where 3 or more accounts hit the same merchant within a 5-minute cluster, distinguishing legitimate links (family/business) from suspicious ones.
- **AI explanations with fallback** — generates one-sentence natural-language explanations via the NVIDIA NIM (Llama 3.1) API, with rule-based templates as an automatic fallback.
- **Explainability 2.0** — provides a confidence gauge, normalized feature-contribution charts, prioritized recommended actions, and a what-if simulator that re-scores hypothetical transaction values.
- **Autonomous ingestion** — polls the Plaid API every 120 seconds via APScheduler with idempotent, deduplicated inserts.
- **Real-time dashboard** — a React UI that polls for new anomalies every 5 seconds and visualizes vendor spending trends with Recharts.
- **Interactive network graph** — a D3.js force-directed graph of accounts, transaction flows, and detected fraud rings with risk-based coloring.
- **Adversarial testing suite** — runs five red-team attack patterns (evasion, flooding, spoofing, temporal, velocity) and produces a weighted robustness score.

---

## Tech Stack

### Backend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.11 | Application runtime |
| Web framework | FastAPI 0.115 | Async REST API with auto-generated OpenAPI docs |
| Server | Uvicorn 0.32 | ASGI server |
| ORM | SQLAlchemy 2.0 | Database models and session management |
| Config | Pydantic Settings 2.6 | Type-safe environment variable validation |
| ML | scikit-learn 1.5 | Isolation Forest + statistical detection |
| Data processing | Pandas 2.2 | Rolling 6-month vendor statistics |
| Scheduling | APScheduler 3.10 | Background transaction ingestion |
| HTTP client | httpx 0.27 | Async calls to the NVIDIA NIM API |
| Data source | plaid-python 9.0 | Plaid Sandbox transaction data |
| Model persistence | joblib 1.4 | Serializing the trained ML model and encoder |

### Frontend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | React 18.3 | Component-based UI |
| Build tool | Vite 5.4 | Dev server and production bundler |
| Styling | TailwindCSS 3.4 | Utility-first dark finance theme |
| Routing | React Router DOM 7.15 | Client-side single-page routing |
| HTTP | Axios 1.7 | Centralized API client |
| Charts | Recharts 2.12 | Trend and feature-contribution charts |
| Network graph | D3.js 7.9 + d3-force 3.0 | Force-directed fraud ring visualization |
| Icons | Lucide React 0.454 | UI iconography |

### Database & DevOps

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Database | SQLite | Embedded persistence (file-based) |
| Backend hosting | Render | Web service with a 1 GB persistent disk for SQLite |
| Frontend hosting | Vercel | Static SPA hosting with CDN and rewrite-based routing |

### Testing

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Test runner | pytest | Unit tests for the explainability engine |
| Adversarial suite | Custom runner | Red-team attack simulations with robustness scoring |

---

## Getting Started

### Prerequisites

- **Python 3.11.9** (pinned in `.python-version` and `backend/runtime.txt`)
- **Node.js 18+** (required for Vite 5)
- **Plaid Sandbox credentials** — a free client ID and secret from [plaid.com](https://plaid.com/)
- **NVIDIA NIM API key** — a free key from [build.nvidia.com](https://build.nvidia.com/) (optional; the system falls back to templates without it)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/Bank-Anomaly-Detection-Engine.git
cd Bank-Anomaly-Detection-Engine
```

**2. Set up the backend**

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # then fill in your credentials
```

**3. Set up the frontend**

```bash
cd ../frontend
npm install
```

Create a `frontend/.env` file with the API URL:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Environment Variables

**Backend** (`backend/.env`):

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `PLAID_CLIENT_ID` | Plaid API client identifier | `5f8a...` | Yes |
| `PLAID_SECRET` | Plaid API secret key | `a1b2c3...` | Yes |
| `PLAID_ENV` | Plaid environment (`sandbox`, `development`, `production`) | `sandbox` | No (defaults to `sandbox`) |
| `PLAID_ACCESS_TOKEN` | Plaid access token for the sandbox account | `access-sandbox-...` | No (defaults to empty) |
| `NVIDIA_NIM_API_KEY` | NVIDIA NIM API key for LLM explanations | `nvapi-...` | Yes |
| `DATABASE_PATH` | Path to the SQLite database file | `./anomalies.db` | No (auto-resolves to `/data/anomalies.db` in production) |
| `ENVIRONMENT` | Application environment (`development`, `production`) | `development` | No (defaults to `development`) |

**Frontend** (`frontend/.env`):

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `VITE_API_URL` | Base URL of the backend API | `http://localhost:8000/api/v1` | No (defaults to `http://localhost:8000/api/v1`) |

### Run Commands

**Backend** (run from `backend/`):

```bash
# Start the development server with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run the unit test suite
python -m pytest tests/
```

The API is then available at `http://localhost:8000`, with interactive OpenAPI docs at `http://localhost:8000/docs`.

**Frontend** (run from `frontend/`):

```bash
# Start the dev server (http://localhost:5173)
npm run dev

# Create a production build
npm run build

# Preview the production build locally
npm run preview
```

---

## Project Structure

```
Bank-Anomaly-Detection-Engine/
├── backend/                  # Python FastAPI application
│   ├── main.py               # App entry point, CORS, core API routes
│   ├── config.py             # Pydantic Settings — single source for env vars
│   ├── requirements.txt      # Pinned Python dependencies
│   ├── runtime.txt           # Python version pin for Render
│   ├── render.yaml           # Render deployment configuration
│   ├── api/                  # Additional API routers (graph, explainability)
│   ├── database/             # SQLAlchemy models and schema migrations
│   ├── ingestion/            # Plaid client and APScheduler ingestion pipeline
│   ├── features/             # Rolling vendor-statistics feature engineering
│   ├── detection/            # Statistical, ML, duplicate, and fraud-ring detectors
│   ├── explainability/       # Confidence, feature contribution, recommender, what-if
│   ├── llm/                  # NVIDIA NIM client, fallback templates, orchestrator
│   ├── scripts/              # Data generation and database reset utilities
│   └── tests/                # Unit tests and the adversarial attack suite
│
├── frontend/                 # React + Vite application
│   ├── src/
│   │   ├── App.jsx           # Root component and React Router routes
│   │   ├── services/         # Centralized Axios API client
│   │   ├── hooks/            # Custom hooks (e.g. useInterval polling)
│   │   ├── components/       # UI components (cards, charts, graph, explainability)
│   │   └── pages/            # Route-level pages (network graph, explainability)
│   ├── vercel.json           # SPA fallback routing for Vercel
│   └── package.json          # Frontend dependencies and scripts
│
└── README.md
```

---

## Architecture Overview

The system is a layered pipeline with a clear separation between data acquisition, detection, explanation, and presentation.

**Data flow from ingestion to dashboard:**

1. **Ingestion** — APScheduler (`ingestion/pipeline.py`) polls the Plaid API every 120 seconds over a 7-day sliding window. Transactions are deduplicated by `plaid_transaction_id` and stored in SQLite.
2. **Feature engineering** — `features/engineer.py` computes a rolling 6-month mean and standard deviation per merchant using Pandas, persisted as `VendorProfile` records.
3. **Detection** — when triggered via `POST /api/v1/detect`, the orchestrator (`detection/orchestrator.py`) runs each unprocessed transaction through three independent layers: statistical Z-Score, Isolation Forest, and duplicate detection. The first layer to fire sets the anomaly type, and all scores are stored.
4. **Explanation** — `llm/explainer.py` generates a natural-language explanation via the NVIDIA NIM API, caching the result in the database and falling back to rule-based templates on any failure.
5. **Serving** — FastAPI exposes REST endpoints under `/api/v1`, including dedicated routers for the network graph and explainability analysis.
6. **Visualization** — the React dashboard polls the API (anomalies every 5s, stats every 10s, transactions every 30s) and renders trends with Recharts and the fraud network with D3.js.

**Notable patterns:**

- **RESTful API** with FastAPI dependency injection (`get_db`) for database sessions.
- **Layered detection pipeline** where each detector is an independent, composable module.
- **Background processing** via a `ThreadPoolExecutor`, keeping CPU-bound detection and ML inference off the async event loop.
- **Graceful degradation** at every external boundary — the ML layer, the LLM API, and sparse-data cases all have safe fallbacks.
- **Caching** — a 30-second in-memory TTL cache on the graph endpoint and database-level caching of LLM explanations.

---

## API Reference

All routes are prefixed with `/api/v1`. The interactive OpenAPI documentation is available at `/docs`. No authentication is currently implemented — all endpoints are public.

| Method | Path | Description | Auth Required |
|--------|------|-------------|:-------------:|
| `GET` | `/` | Root health check for deployment platforms | No |
| `GET` | `/api/v1/health` | Health status with timestamp and version | No |
| `GET` | `/api/v1/transactions` | Paginated list of transactions | No |
| `GET` | `/api/v1/anomalies` | Paginated anomalies with embedded transaction data | No |
| `GET` | `/api/v1/stats` | Dashboard KPIs (totals, flag rate, top anomaly type) | No |
| `POST` | `/api/v1/detect` | Trigger anomaly detection in the background | No |
| `GET` | `/api/v1/detect/status` | Status of the last detection run | No |
| `GET` | `/api/v1/rings` | Detected fraud rings within a time window | No |
| `GET` | `/api/v1/accounts` | Accounts with user profiles and link counts | No |
| `POST` | `/api/v1/tests/adversarial` | Run the adversarial test suite | No |
| `GET` | `/api/v1/tests/adversarial/last` | Retrieve cached adversarial test results | No |
| `GET` | `/api/v1/anomalies/{id}/explain` | Full Explainability 2.0 analysis for an anomaly | No |
| `POST` | `/api/v1/anomalies/{id}/feedback` | Record analyst feedback on an anomaly | No |
| `GET` | `/api/v1/anomalies/{id}/what-if` | Re-score an anomaly with hypothetical values | No |
| `GET` | `/api/v1/graph/network` | Network graph nodes, edges, and rings | No |

---

## Roadmap

- [x] Dual-layer statistical and ML anomaly detection
- [x] Cross-account fraud ring detection
- [x] AI explanations with rule-based fallback
- [x] Explainability 2.0 (confidence, feature contributions, what-if)
- [x] Real-time dashboard and D3 network graph
- [x] Adversarial testing suite
- [ ] Authentication and role-based access control (JWT)
- [ ] Anomaly resolution workflow (mark resolved / false positive in the UI)
- [ ] Real-time updates via Server-Sent Events to replace polling
- [ ] PostgreSQL migration with async SQLAlchemy for concurrent writes
- [ ] CI/CD pipeline with automated testing and dependency scanning

---

## Contributing

Contributions are welcome. Please follow the standard fork-and-pull-request workflow:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make your changes, following the existing code conventions.
4. Run the backend tests before submitting: `cd backend && python -m pytest tests/`.
5. Verify the frontend builds cleanly: `cd frontend && npm run build`.
6. Commit your changes and push the branch: `git push -u origin feature/your-feature`.
7. Open a pull request with a clear description of the change and how it was tested.

---

## License

This project is licensed under the MIT License. No `LICENSE` file is currently present in the repository — add one to formalize the terms.
