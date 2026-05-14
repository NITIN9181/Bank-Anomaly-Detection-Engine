"""
FastAPI application for Bank Anomaly Detection Engine.

Provides RESTful API endpoints for transaction management and anomaly detection.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database.models import Anomaly, SessionLocal, Transaction, create_tables
from detection.orchestrator import run_detection
from llm.explainer import explain_all_new_anomalies

from config import settings

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

# CORS restricted to known domains.
# Update origins list with your Vercel URL after first deploy.
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
]

# Add production Vercel domain if configured
if settings.ENVIRONMENT == "production":
    # Replace with your actual Vercel URL after deployment
    origins.append("https://your-app.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


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
    """
    logger.info("Starting Bank Anomaly Detection Engine")
    
    # Create database tables
    create_tables()
    logger.info("Database tables initialized")
    
    # Start ingestion scheduler
    try:
        from ingestion.pipeline import start_ingestion
        start_ingestion()
        logger.info("Transaction ingestion scheduler started")
    except Exception as e:
        logger.error(f"Failed to start ingestion scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Application shutdown event handler.
    
    - Gracefully stops transaction ingestion scheduler
    """
    logger.info("Shutting down Bank Anomaly Detection Engine")
    
    try:
        from ingestion.pipeline import stop_ingestion
        stop_ingestion()
        logger.info("Transaction ingestion scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping ingestion scheduler: {e}")


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


@app.post("/api/v1/detect")
async def trigger_detection(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Trigger anomaly detection on all unprocessed transactions.
    
    Runs multi-layer detection (statistical + ML + duplicate) and generates
    LLM explanations for newly flagged anomalies.
    
    Args:
        db: Database session
    
    Returns:
        Detection results summary with counts
    """
    logger.info("Manual detection triggered via API")
    
    # Run detection pipeline
    new_anomalies = run_detection(db)
    
    # Generate explanations for new anomalies
    explained_count = await explain_all_new_anomalies(db)
    
    return {
        "processed": len(new_anomalies),
        "new_anomalies": len(new_anomalies),
        "explained": explained_count
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
        # Get transaction via relationship
        txn = db.query(Transaction).get(a.transaction_id)
        
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
