"""
FastAPI application for Bank Anomaly Detection Engine.

Provides RESTful API endpoints for transaction management and anomaly detection.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import Depends, FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database.models import Anomaly, SessionLocal, Transaction, create_tables, AccountLink
from detection.orchestrator import run_detection
from llm.explainer import explain_all_new_anomalies

from config import settings

# Import API routers
from api.graph import router as graph_router
from api.explainability import router as explain_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Bank Anomaly Detection Engine",
    version="1.0.0",
    description="Autonomous real-time reconciliation and fraud detection across banking data streams"
)

# CORS configuration - MUST be added before routers
# Allow localhost for development and Vercel domain for production
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
    "https://bank-anomaly-detection-engine.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register API routers
app.include_router(graph_router, prefix="/api/v1")
app.include_router(explain_router, prefix="/api/v1")


# Dependency: Database session
def get_db() -> Session:
    """
    Dependency that provides a database session.
    
    Yields:
        SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event() -> None:
    """
    Application startup event handler.
    
    - Creates database tables if they don't exist
    - Starts transaction ingestion scheduler
    
    Note: Model training is deferred to first detection run to speed up startup
    and pass Render health checks faster.
    """
    logger.info("Starting Bank Anomaly Detection Engine")
    
    # Create database tables
    create_tables()
    logger.info("Database tables initialized")
    
    # Start ingestion scheduler (lightweight, non-blocking)
    try:
        from ingestion.pipeline import start_ingestion
        start_ingestion()
        logger.info("Transaction ingestion scheduler started")
    except Exception as e:
        logger.error(f"Failed to start ingestion scheduler: {e}")
    
    logger.info("Startup complete - ready to accept requests")
    logger.info("Note: ML model will be trained on first detection run")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Application shutdown event handler.
    
    - Gracefully stops transaction ingestion scheduler
    - Shuts down background task executor
    """
    logger.info("Shutting down Bank Anomaly Detection Engine")
    
    try:
        from ingestion.pipeline import stop_ingestion
        stop_ingestion()
        logger.info("Transaction ingestion scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping ingestion scheduler: {e}")
    
    # Shutdown thread pool
    try:
        executor.shutdown(wait=False)
        logger.info("Background task executor stopped")
    except Exception as e:
        logger.error(f"Error stopping executor: {e}")


@app.get("/")
async def root() -> dict[str, Any]:
    """
    Root endpoint - quick health check for deployment platforms.
    
    Returns:
        Basic status information
    """
    return {
        "service": "Bank Anomaly Detection Engine",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/v1/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Health status with timestamp and version
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }


@app.get("/api/v1/transactions")
async def list_transactions(
    limit: int = Query(default=50, ge=1, le=200, description="Number of transactions to return"),
    offset: int = Query(default=0, ge=0, description="Number of transactions to skip"),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    List transactions with pagination.
    
    Args:
        limit: Maximum number of transactions to return (1-200)
        offset: Number of transactions to skip
        db: Database session
    
    Returns:
        Paginated transaction list with metadata
    """
    # Get total count
    total = db.query(Transaction).count()
    
    # Fetch paginated transactions ordered by date DESC
    transactions = db.query(Transaction).order_by(
        Transaction.date.desc(),
        Transaction.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    # Serialize transactions
    items = [
        {
            "id": txn.id,
            "plaid_transaction_id": txn.plaid_transaction_id,
            "amount": txn.amount,
            "date": txn.date,
            "merchant_name": txn.merchant_name,
            "category": txn.category,
            "created_at": txn.created_at.isoformat() + "Z" if txn.created_at else None
        }
        for txn in transactions
    ]
    
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }


# Global state for detection status
detection_status = {
    "running": False,
    "last_run": None,
    "last_result": None
}
# Lock to protect detection_status from concurrent read/write races
_detection_status_lock = threading.Lock()

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=2)


def run_detection_background(db_session):
    """
    Run detection in background thread to avoid blocking the main event loop.
    """
    global detection_status
    
    try:
        with _detection_status_lock:
            detection_status["running"] = True
        logger.info("Background detection started")
        
        # Run detection pipeline
        new_anomalies = run_detection(db_session)
        
        # Generate explanations (this is async but we're in a thread)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        explained_count = loop.run_until_complete(explain_all_new_anomalies(db_session))
        loop.close()
        
        result = {
            "processed": len(new_anomalies),
            "new_anomalies": len(new_anomalies),
            "explained": explained_count,
            "completed_at": datetime.utcnow().isoformat() + "Z"
        }
        
        with _detection_status_lock:
            detection_status["last_result"] = result
            detection_status["last_run"] = datetime.utcnow()
        logger.info(f"Background detection completed: {result}")
        
    except Exception as e:
        logger.error(f"Background detection failed: {e}", exc_info=True)
        with _detection_status_lock:
            detection_status["last_result"] = {
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat() + "Z"
            }
    finally:
        with _detection_status_lock:
            detection_status["running"] = False
        db_session.close()


@app.post("/api/v1/detect")
async def trigger_detection(background_tasks: BackgroundTasks) -> dict[str, Any]:
    """
    Trigger anomaly detection on all unprocessed transactions.
    
    Runs detection in background to avoid timeout issues.
    Use GET /api/v1/detect/status to check progress.
    
    Returns:
        Immediate acknowledgment that detection has started
    """
    global detection_status
    
    if detection_status["running"]:
        return {
            "status": "already_running",
            "message": "Detection is already in progress",
            "started_at": detection_status.get("last_run")
        }    
    logger.info("Manual detection triggered via API - running in background")
    
    # Create a new database session for the background task
    db = SessionLocal()
    
    # Submit to thread pool instead of FastAPI background tasks
    # This prevents blocking the event loop
    executor.submit(run_detection_background, db)
    
    return {
        "status": "started",
        "message": "Detection started in background. Check /api/v1/detect/status for progress.",
        "started_at": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/api/v1/detect/status")
async def get_detection_status() -> dict[str, Any]:
    """
    Get the status of the last detection run.
    
    Returns:
        Detection status and results
    """
    return {
        "running": detection_status["running"],
        "last_run": detection_status["last_run"].isoformat() + "Z" if detection_status["last_run"] else None,
        "last_result": detection_status["last_result"]
    }


@app.get("/api/v1/anomalies")
async def list_anomalies(
    status: str = Query(
        default="flagged",
        description="Filter by status (flagged, resolved, false_positive)"
    ),
    limit: int = Query(default=50, ge=1, le=200, description="Number of results"),
    offset: int = Query(default=0, ge=0, description="Number to skip"),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    List anomalies with optional status filter and pagination.
    
    Returns anomalies with embedded transaction data and explanations.
    
    Args:
        status: Filter by anomaly status
        limit: Maximum number of anomalies to return
        offset: Number of anomalies to skip
        db: Database session
    
    Returns:
        Paginated anomaly list with embedded transaction data
    """
    # Validate status
    valid_statuses = ["flagged", "resolved", "false_positive"]
    if status not in valid_statuses:
        status = "flagged"
    
    # Query with eager loading of transaction relationship
    query = db.query(Anomaly).filter(Anomaly.status == status)
    total = query.count()
    
    anomalies = query.options(
        joinedload(Anomaly.transaction)
    ).order_by(
        Anomaly.detected_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Serialize results
    items = []
    for a in anomalies:
        # Use the already-loaded relationship instead of a second query
        txn = a.transaction
        
        items.append({
            "id": a.id,
            "transaction": {
                "id": txn.id if txn else None,
                "amount": txn.amount if txn else 0.0,
                "date": txn.date if txn else None,
                "merchant_name": txn.merchant_name if txn else "Unknown",
            },
            "anomaly_type": a.anomaly_type,
            "z_score": a.z_score,
            "isolation_score": a.isolation_score,
            "explanation": a.explanation,
            "detected_at": a.detected_at.isoformat() + "Z" if a.detected_at else None,
            "status": a.status,
            "explanation_confidence": getattr(a, "explanation_confidence", 0.0),
        })
    
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/api/v1/stats")
async def get_stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Get dashboard statistics and KPIs.
    
    Returns:
        Dashboard statistics including transaction counts, anomaly rates,
        and top anomalous vendor
    """
    # Total counts
    total_txns = db.query(Transaction).count()
    total_anomalies = db.query(Anomaly).count()
    flagged = db.query(Anomaly).filter(Anomaly.status == "flagged").count()
    
    # Calculate flag rate
    flag_rate = (flagged / total_txns * 100) if total_txns > 0 else 0.0
    
    # Top anomalous vendor (most common anomaly type)
    top_vendor_result = (
        db.query(Anomaly.anomaly_type, func.count(Anomaly.id).label("count"))
        .group_by(Anomaly.anomaly_type)
        .order_by(func.count(Anomaly.id).desc())
        .first()
    )
    top_vendor = top_vendor_result[0] if top_vendor_result else None
    
    # Last ingestion time (from most recent transaction)
    last_txn = db.query(Transaction).order_by(
        Transaction.created_at.desc()
    ).first()
    last_ingestion = None
    if last_txn and last_txn.created_at:
        last_ingestion = last_txn.created_at.isoformat() + "Z"
    
    return {
        "total_transactions": total_txns,
        "total_anomalies": total_anomalies,
        "flag_rate_percent": round(flag_rate, 2),
        "top_anomalous_vendor": top_vendor,
        "last_ingestion_at": last_ingestion,
        "model_version": "isolation_forest_v1"
    }


@app.get("/api/v1/rings")
async def list_fraud_rings(
    window_hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    Detect and return potential fraud rings across accounts.
    
    Analyzes cross-account transaction patterns to identify coordinated
    spending that may indicate fraud rings or money laundering.
    
    Args:
        window_hours: Time window to analyze (1-168 hours)
        db: Database session
    
    Returns:
        List of detected fraud rings with risk scores
    """
    from detection.fraud_ring import detect_fraud_ring
    
    rings = detect_fraud_ring(db, window_hours)
    
    return {
        "items": rings,
        "total": len(rings),
        "window_hours": window_hours
    }


@app.get("/api/v1/accounts")
async def list_accounts(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    List all accounts with user profiles and link counts.
    
    Returns:
        List of accounts with embedded user information
    """
    from database.models import Account, User
    
    accounts = db.query(Account).all()
    
    items = []
    for account in accounts:
        # Get user
        user = db.query(User).get(account.user_id)
        
        # Count links
        link_count = (
            db.query(AccountLink).filter(
                (AccountLink.account_a_id == account.id) |
                (AccountLink.account_b_id == account.id)
            ).count()
        )
        
        items.append({
            "id": account.id,
            "account_id": account.account_id,
            "user": {
                "name": user.name if user else "Unknown",
                "risk_profile": user.risk_profile if user else "medium",
                "typical_monthly_spend": user.typical_monthly_spend if user else 0.0
            },
            "account_type": account.account_type,
            "balance": account.balance,
            "link_count": link_count,
            "created_at": account.created_at.isoformat() + "Z" if account.created_at else None
        })
    
    return {
        "items": items,
        "total": len(items)
    }


@app.post("/api/v1/tests/adversarial")
async def run_adversarial_tests(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Run adversarial test suite against detection system.
    
    Executes 5 attack patterns to test system robustness:
    - Evasion: Gradual amount increase
    - Flooding: Hide anomalies in noise
    - Spoofing: Merchant name obfuscation
    - Temporal: Backdated transactions
    - Velocity: Burst spending
    
    WARNING: This modifies database with synthetic attack data.
    In production, this should run in an isolated transaction.
    
    Args:
        db: Database session
    
    Returns:
        Complete test results with robustness score and vulnerability report
    """
    from tests.adversarial.runner import run_all_adversarial_tests
    
    logger.info("Adversarial test suite triggered via API")
    
    # Run all tests
    results = run_all_adversarial_tests(db)
    
    return {
        "message": "Adversarial tests complete. Review results for vulnerabilities.",
        "warning": "Tests inserted synthetic data. Consider running in isolated transaction.",
        **results
    }


@app.get("/api/v1/tests/adversarial/last")
async def get_last_test_results(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Retrieve cached results from last adversarial test run.
    
    NOTE: Current implementation returns placeholder.
    In production, implement caching layer (Redis) to store test results.
    
    Args:
        db: Database session
    
    Returns:
        Cached test results or placeholder
    """
    return {
        "note": "Implement caching layer (Redis) for production",
        "timestamp": None,
        "results": None,
        "recommendation": "Use POST /api/v1/tests/adversarial to run tests"
    }
