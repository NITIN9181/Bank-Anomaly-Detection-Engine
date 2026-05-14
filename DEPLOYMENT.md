# Deployment Guide - Production Ready

## Prerequisites

Before deploying, you need:

1. **Plaid Credentials** (from [dashboard.plaid.com](https://dashboard.plaid.com))
   - ✅ `PLAID_CLIENT_ID`
   - ✅ `PLAID_SECRET`
   - ✅ `PLAID_ACCESS_TOKEN` (generate using `backend/generate_plaid_token.py`)

2. **NVIDIA NIM API Key** (from [build.nvidia.com](https://build.nvidia.com))
   - ✅ `NVIDIA_NIM_API_KEY` (starts with `nvapi-`)

3. **GitHub Account** (for connecting to Render/Vercel)

4. **Render Account** (free tier at [render.com](https://render.com))

5. **Vercel Account** (free tier at [vercel.com](https://vercel.com))

---

## Step 1: Generate Plaid Access Token (Local)

**IMPORTANT**: You must generate the access token locally before deploying.

1. Open `backend/generate_plaid_token.py`
2. Replace `YOUR_CLIENT_ID` and `YOUR_SECRET` with your actual Plaid credentials
3. Run the script:

```bash
cd backend
python generate_plaid_token.py
```

4. **Copy the access token** it prints (looks like `access-sandbox-xxxxx-xxxxx`)
5. Save it - you'll need it for Render environment variables

**Expected Output**:
```
Creating sandbox public token...
✓ Public token created: public-sandbox-xxxxx...
Exchanging for access token...

============================================================
SUCCESS! Your Plaid Access Token:
============================================================

access-sandbox-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx

============================================================
Add this to your backend/.env file:
PLAID_ACCESS_TOKEN=access-sandbox-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx
============================================================
```

---

## Step 2: Test Locally (Verify Before Deploy)

Before deploying to production, test everything works locally:

1. **Update `backend/.env`** with all credentials:

```bash
PLAID_CLIENT_ID=your_actual_client_id
PLAID_SECRET=your_actual_secret
PLAID_ACCESS_TOKEN=access-sandbox-xxxxx-xxxxx  # From Step 1
PLAID_ENV=sandbox

NVIDIA_NIM_API_KEY=nvapi-your_actual_key

DATABASE_PATH=./anomalies.db
ENVIRONMENT=development
```

2. **Start backend**:

```bash
cd backend
.venv\Scripts\activate  # Windows
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Verify backend is working**:
   - Open http://localhost:8000/api/v1/health
   - Should return: `{"status": "ok", ...}`
   - Check logs for: `"Fetched X transactions"` (proves Plaid works)

4. **Start frontend**:

```bash
cd frontend
npm run dev
```

5. **Verify frontend is working**:
   - Open http://localhost:3000
   - Should see green "Live" indicator
   - Should see transactions in the feed
   - Click "Run Detection" - anomalies should appear

**If local testing fails, DO NOT deploy yet. Fix issues first.**

---

## Step 3: Deploy Backend to Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New → Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `bank-anomaly-engine`
   - **Runtime**: `Python 3`
   - **Root Directory**: `backend/`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):

   ```
   PLAID_CLIENT_ID=your_actual_client_id
   PLAID_SECRET=your_actual_secret
   PLAID_ACCESS_TOKEN=access-sandbox-xxxxx-xxxxx  # From Step 1
   PLAID_ENV=sandbox
   
   NVIDIA_NIM_API_KEY=nvapi-your_actual_key
   
   DATABASE_PATH=/data/anomalies.db
   ENVIRONMENT=production
   ```

6. **Add Persistent Disk** (for SQLite database):
   - Click "Add Disk"
   - **Name**: `data`
   - **Mount Path**: `/data`
   - **Size**: `1 GB` (free tier)

7. **Set Health Check**:
   - **Health Check Path**: `/api/v1/health`

8. Click **Create Web Service**

9. **Wait for deployment** (~5 minutes)
   - Watch logs for: `"Application startup complete"`
   - Watch logs for: `"Fetched X transactions"` (proves Plaid works)

10. **Copy your Render URL**: `https://bank-anomaly-engine-xxxxx.onrender.com`

---

## Step 4: Verify Backend Deployment

Test your deployed backend:

```bash
# Test health endpoint
curl https://your-render-url.onrender.com/api/v1/health

# Expected response:
{"status":"ok","timestamp":"2026-05-14T...","version":"1.0.0"}

# Test transactions endpoint
curl https://your-render-url.onrender.com/api/v1/transactions

# Should return array of transactions from Plaid sandbox
```

**If you get errors**:
- Check Render logs for Python errors
- Verify all environment variables are set correctly
- Verify `PLAID_ACCESS_TOKEN` is the one from Step 1
- Check disk is mounted at `/data`

---

## Step 5: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **Add New Project**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend/`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. **Add Environment Variable**:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://your-render-url.onrender.com/api/v1` (from Step 3)

6. Click **Deploy**

7. **Wait for deployment** (~2 minutes)

8. **Copy your Vercel URL**: `https://bank-anomaly-dashboard-xxxxx.vercel.app`

---

## Step 6: Update CORS (Critical!)

After deploying frontend, you MUST update backend CORS to allow your Vercel domain:

1. Open `backend/main.py` in your code editor
2. Find the CORS section (around line 30)
3. Add your Vercel URL to the production origins:

```python
# CORS restricted to known domains.
# Update origins list with your Vercel URL after first deploy.
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

if settings.ENVIRONMENT == "production":
    origins.append("https://bank-anomaly-dashboard-xxxxx.vercel.app")  # ← ADD YOUR VERCEL URL HERE
```

4. **Commit and push**:

```bash
git add backend/main.py
git commit -m "Update CORS with Vercel URL"
git push origin main
```

5. **Wait for Render to auto-redeploy** (~3 minutes)

---

## Step 7: Verify Full Deployment

Open your Vercel URL in a browser and verify:

- ✅ Dashboard loads without errors
- ✅ Green "Live" indicator in navbar (proves backend connection)
- ✅ Stats bar shows numbers (proves API working)
- ✅ Transaction feed shows data (proves Plaid integration)
- ✅ Click "Run Detection" button
- ✅ Anomaly cards appear on right side (proves detection working)
- ✅ Click "View Trend" on an anomaly (proves charts working)
- ✅ LLM explanations appear (proves NVIDIA NIM working)

**Open browser DevTools (F12) and check Console**:
- Should have NO red errors
- Should see polling logs every 5-10 seconds

---

## Troubleshooting

### Backend won't start on Render

**Error**: `ModuleNotFoundError` or build fails

**Fix**:
- Check `requirements.txt` has all dependencies
- Verify Python version is 3.11+
- Check Render logs for specific error
- Ensure Root Directory is set to `backend/`

---

**Error**: `Plaid client not configured: Access token not set`

**Fix**:
- Verify `PLAID_ACCESS_TOKEN` environment variable is set in Render
- Make sure you used the token from `generate_plaid_token.py`
- Restart Render service after adding environment variables

---

**Error**: Database errors or `no such table`

**Fix**:
- Verify disk is mounted at `/data`
- Check `DATABASE_PATH=/data/anomalies.db` in environment variables
- Database tables are created automatically on first startup

---

### Frontend shows "Offline" on Vercel

**Error**: Red "Offline" indicator in navbar

**Fix**:
1. Verify `VITE_API_URL` is set correctly in Vercel environment variables
2. Test backend health endpoint directly: `curl https://your-render-url.onrender.com/api/v1/health`
3. Check CORS is configured with your Vercel URL in `backend/main.py`
4. Open browser DevTools → Console → Look for CORS errors
5. If you see CORS errors, update `backend/main.py` and redeploy

---

**Error**: `Failed to fetch` or network errors

**Fix**:
- Render free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Refresh page after 30 seconds
- Consider upgrading to Render Starter ($7/mo) for always-on

---

### No transactions appearing

**Error**: Transaction feed is empty

**Fix**:
1. Check Render logs for ingestion errors
2. Verify Plaid credentials are correct
3. Test Plaid endpoint: `curl https://your-render-url.onrender.com/api/v1/transactions`
4. Plaid sandbox has synthetic data - should see transactions immediately
5. If still empty, check Render logs for: `"Fetched X transactions"`

---

### Anomalies not generating explanations

**Error**: Anomaly cards show "No explanation available"

**Fix**:
1. Check `NVIDIA_NIM_API_KEY` is set in Render environment variables
2. Verify API key is valid at [build.nvidia.com](https://build.nvidia.com)
3. Check Render logs for LLM errors
4. **Fallback templates work even if LLM fails** - you should still see explanations like:
   > "This $5,000 charge to AWS is 4.75 standard deviations above your 6-month average."

---

### Render service keeps crashing

**Error**: Service restarts repeatedly

**Fix**:
- Check Render logs for Python exceptions
- Verify all environment variables are set
- Check memory usage (free tier has 512 MB limit)
- Ensure health check path is `/api/v1/health`
- If using too much memory, upgrade to Starter plan

---

### Vercel build fails

**Error**: Build fails during deployment

**Fix**:
- Verify Root Directory is set to `frontend/`
- Check `package.json` has all dependencies
- Ensure Build Command is `npm run build`
- Ensure Output Directory is `dist`
- Check Vercel logs for specific error

---

## Post-Deployment Checklist

Use this checklist to verify your deployment is working:

### Backend (Render)
- [ ] Service shows "Live" status in Render dashboard
- [ ] Health check passes: `curl https://your-render-url.onrender.com/api/v1/health`
- [ ] Transactions endpoint returns data: `curl https://your-render-url.onrender.com/api/v1/transactions`
- [ ] Logs show: `"Application startup complete"`
- [ ] Logs show: `"Fetched X transactions"` (proves Plaid works)
- [ ] Logs show: `"Ingestion scheduler started"`
- [ ] No Python exceptions in logs
- [ ] Disk mounted at `/data` (check Render dashboard)

### Frontend (Vercel)
- [ ] Deployment shows "Ready" status in Vercel dashboard
- [ ] Site loads without errors
- [ ] Green "Live" indicator in navbar
- [ ] Stats bar shows numbers (not zeros)
- [ ] Transaction feed shows data
- [ ] No console errors in browser DevTools (F12)
- [ ] No CORS errors in browser console

### Integration
- [ ] CORS configured with Vercel URL in `backend/main.py`
- [ ] Frontend can fetch from backend (check Network tab in DevTools)
- [ ] Click "Run Detection" button works
- [ ] Anomaly cards appear after detection
- [ ] Click "View Trend" opens modal with chart
- [ ] LLM explanations appear on anomaly cards
- [ ] Browser tab flashes on new anomalies

### Credentials
- [ ] `PLAID_CLIENT_ID` set in Render
- [ ] `PLAID_SECRET` set in Render
- [ ] `PLAID_ACCESS_TOKEN` set in Render (from `generate_plaid_token.py`)
- [ ] `NVIDIA_NIM_API_KEY` set in Render
- [ ] `VITE_API_URL` set in Vercel (points to Render URL)

---

## Cost Breakdown

| Service | Plan | Cost | Limits |
|---------|------|------|--------|
| Render | Free | $0 | 750 hrs/mo, sleeps after 15 min |
| Vercel | Hobby | $0 | 100 GB bandwidth/mo |
| Plaid | Sandbox | $0 | Synthetic data only |
| NVIDIA NIM | Free | $0 | Rate limits apply |
| **Total** | | **$0/month** | |

---

## Production Upgrade Path

When ready to scale beyond free tier:

1. **Render**: Upgrade to Starter ($7/mo)
   - No sleep, always-on
   - 512 MB RAM → 2 GB RAM
   - Faster cold starts

2. **Database**: Migrate to PostgreSQL
   - Render Managed PostgreSQL ($7/mo)
   - Concurrent writes
   - Better performance at scale

3. **Vercel**: Upgrade to Pro ($20/mo)
   - More bandwidth
   - Advanced analytics
   - Team collaboration

4. **Plaid**: Upgrade to Development ($0, then Production)
   - Real bank connections
   - Production-grade security

5. **NVIDIA NIM**: Upgrade to paid tier
   - Higher rate limits
   - SLA guarantees

**Total Production Cost**: ~$34/month for small-scale production

## Monitoring & Maintenance

### Render Monitoring

- **Logs**: Dashboard → Your Service → Logs (real-time)
- **Metrics**: Dashboard → Your Service → Metrics (CPU, memory, requests)
- **Health Checks**: Automatic every 5 minutes at `/api/v1/health`
- **Alerts**: Configure email alerts for service down/errors

### Vercel Monitoring

- **Deployments**: Dashboard → Your Project → Deployments
- **Analytics**: Dashboard → Your Project → Analytics (page views, errors)
- **Function Logs**: Real-time logs for serverless functions
- **Performance**: Core Web Vitals tracking

### External Monitoring (Optional)

Use [UptimeRobot](https://uptimerobot.com) (free tier):
1. Create new monitor
2. Monitor Type: HTTP(s)
3. URL: `https://your-render-url.onrender.com/api/v1/health`
4. Monitoring Interval: 5 minutes
5. Alert Contacts: Your email
6. Get notified when service goes down

---

## Updating After Changes

### Backend Changes

```bash
# Make your changes to backend code
git add backend/
git commit -m "Update backend logic"
git push origin main
```

**Render auto-deploys** on push to main branch (~3 minutes).

Watch deployment: Render Dashboard → Your Service → Events

---

### Frontend Changes

```bash
# Make your changes to frontend code
git add frontend/
git commit -m "Update frontend UI"
git push origin main
```

**Vercel auto-deploys** on push to main branch (~2 minutes).

Watch deployment: Vercel Dashboard → Your Project → Deployments

---

### Environment Variable Changes

**Render**:
1. Dashboard → Your Service → Environment
2. Edit or add variables
3. Click "Save Changes"
4. Service automatically restarts

**Vercel**:
1. Dashboard → Your Project → Settings → Environment Variables
2. Edit or add variables
3. Click "Save"
4. Redeploy: Deployments → Latest → "Redeploy"

---

## Demo Video Recording (Optional)

Create a demo video to showcase your project:

1. Open your deployed dashboard in browser
2. Start screen recording (Loom, OBS, QuickTime, or Windows Game Bar)
3. **Script** (90 seconds):
   - "This is the Bank Anomaly Detection Engine - a real-time fraud detection system"
   - Show stats bar with KPIs (total transactions, anomalies, detection rate)
   - Scroll transaction feed showing recent transactions
   - Click "Run Detection" button
   - Show anomaly cards appearing on right side
   - Click "View Trend" on an anomaly
   - Explain the chart and anomaly highlight
   - Show LLM explanation of why it's anomalous
   - Mention tech stack: "Built with FastAPI, React, Isolation Forest ML, and NVIDIA NIM for AI explanations"
4. Upload to Loom/YouTube
5. Add link to `README.md` under "Live Demo" section

---

## Summary: Your Deployment Journey

### What You Built
- ✅ **Backend API**: FastAPI with dual-layer anomaly detection (Statistical + ML)
- ✅ **Frontend Dashboard**: React with real-time polling and interactive charts
- ✅ **Plaid Integration**: Real sandbox transaction data
- ✅ **AI Explanations**: NVIDIA NIM LLM with fallback templates
- ✅ **Production Ready**: Deployed on Render + Vercel (free tier)

### What You Learned
- Setting up Plaid Sandbox for financial data
- Building ML-powered anomaly detection
- Integrating LLM APIs for natural language explanations
- Deploying full-stack apps to cloud platforms
- Configuring CORS for production
- Managing environment variables securely

### Next Steps
1. **Share your project**: Add demo video to README
2. **Monitor performance**: Set up UptimeRobot alerts
3. **Iterate**: Add features like email alerts, custom rules, or multi-user support
4. **Scale**: Upgrade to paid tiers when ready for production traffic
5. **Portfolio**: Add to your resume/portfolio with live demo link

---

## Need Help?

- **Render Issues**: [render.com/docs](https://render.com/docs)
- **Vercel Issues**: [vercel.com/docs](https://vercel.com/docs)
- **Plaid Issues**: [plaid.com/docs](https://plaid.com/docs)
- **NVIDIA NIM Issues**: [build.nvidia.com](https://build.nvidia.com)

---

**Congratulations! Your Bank Anomaly Detection Engine is now live in production! 🎉**
