# Quick Start Guide - Get It Working in 10 Minutes

## Prerequisites

You need:
- ✅ Plaid client_id and secret (you have these!)
- ⏳ NVIDIA NIM API key (get from [build.nvidia.com](https://build.nvidia.com))
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed

---

## Step 1: Generate Plaid Access Token (2 minutes)

1. Open `backend/generate_plaid_token.py`
2. Replace `YOUR_CLIENT_ID` and `YOUR_SECRET` with your actual credentials
3. Run the script:

```bash
cd backend
python generate_plaid_token.py
```

4. Copy the access token it prints (looks like `access-sandbox-xxxxx-xxxxx`)

---

## Step 2: Configure Backend Environment (1 minute)

1. Copy the environment template:

```bash
cd backend
copy .env.example .env
```

2. Open `backend/.env` and fill in:

```bash
PLAID_CLIENT_ID=your_actual_client_id
PLAID_SECRET=your_actual_secret
PLAID_ENV=sandbox
PLAID_ACCESS_TOKEN=access-sandbox-xxxxx-xxxxx  # From Step 1

NVIDIA_NIM_API_KEY=nvapi-your_key_here  # Get from build.nvidia.com

DATABASE_PATH=./anomalies.db
ENVIRONMENT=development
```

---

## Step 3: Start Backend (2 minutes)

```bash
cd backend

# Activate virtual environment
..\.venv\Scripts\activate

# Start server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting Bank Anomaly Detection Engine
INFO:     Database tables initialized
INFO:     Plaid client initialized for environment: sandbox
INFO:     Ingestion scheduler started (120-second interval)
INFO:     Running initial ingestion
INFO:     Fetched X transactions
INFO:     Application startup complete.
```

✅ Backend is running!

---

## Step 4: Configure Frontend (1 minute)

```bash
cd frontend
copy .env.example .env
```

Open `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Step 5: Start Frontend (2 minutes)

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.4.21  ready in 1736 ms
➜  Local:   http://localhost:3000/
```

✅ Frontend is running!

---

## Step 6: Open Dashboard (1 minute)

1. Open browser: **http://localhost:3000**
2. You should see:
   - ✅ Green "Live" indicator (backend connected)
   - ✅ Stats bar with numbers
   - ✅ Transaction feed with data
   - ✅ Empty anomaly panel (no anomalies yet)

---

## Step 7: Run Detection (1 minute)

1. Click the **"Run Detection"** button in the dashboard
2. Wait a few seconds
3. Anomaly cards should appear on the right side
4. Each card shows:
   - Merchant name and amount
   - Color-coded badge (red/amber/violet)
   - LLM explanation
   - "View Trend" button

---

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Fix**: Install dependencies
```bash
cd backend
..\.venv\Scripts\activate
pip install -r requirements.txt
```

---

### No transactions appearing

**Error**: `Plaid client not configured: Access token not set`

**Fix**: Make sure you:
1. Ran `generate_plaid_token.py`
2. Added `PLAID_ACCESS_TOKEN` to `.env`
3. Restarted backend server

---

### Frontend shows "Offline"

**Fix**: 
1. Check backend is running on port 8000
2. Check `frontend/.env` has correct `VITE_API_URL`
3. Restart frontend: `npm run dev`

---

### Anomalies not generating explanations

**Error**: LLM API fails

**Fix**: This is OK! The system has fallback templates. You'll still see explanations like:
> "This $5,000 charge to AWS is 4.75 standard deviations above your 6-month average."

To fix properly:
1. Get NVIDIA NIM API key from [build.nvidia.com](https://build.nvidia.com)
2. Add to `backend/.env` as `NVIDIA_NIM_API_KEY`
3. Restart backend

---

## Get NVIDIA NIM API Key (Optional but Recommended)

1. Go to [build.nvidia.com](https://build.nvidia.com)
2. Sign up (free)
3. Go to API Keys section
4. Generate new API key
5. Copy key (starts with `nvapi-`)
6. Add to `backend/.env`

---

## What's Next?

### Local Development ✅
You're all set! The system is running locally with:
- Real Plaid Sandbox data
- Dual-layer anomaly detection
- LLM explanations (or fallback templates)
- Real-time dashboard

### Deploy to Production 🚀
When ready, follow `DEPLOYMENT.md` to deploy to:
- **Backend**: Render (free tier)
- **Frontend**: Vercel (free tier)
- **Total cost**: $0/month

---

## Quick Commands Reference

### Start Backend
```bash
cd backend
..\.venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Generate New Plaid Token
```bash
cd backend
python generate_plaid_token.py
```

### Check Backend Health
```bash
curl http://localhost:8000/api/v1/health
```

### Check Transactions
```bash
curl http://localhost:8000/api/v1/transactions
```

### Trigger Detection Manually
```bash
curl -X POST http://localhost:8000/api/v1/detect
```

---

## Success! 🎉

Your Bank Anomaly Detection Engine is now running locally with:
- ✅ Plaid Sandbox integration
- ✅ Real transaction data
- ✅ Anomaly detection (Statistical + ML)
- ✅ LLM explanations
- ✅ Real-time dashboard
- ✅ Vendor trend charts

**Next**: Follow `DEPLOYMENT.md` to deploy to production (Render + Vercel)
