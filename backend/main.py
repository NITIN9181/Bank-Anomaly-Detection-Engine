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
from sqlalchemy.orm import Session

from database.models import SessionLocal, Transaction, create_tables

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

# CORS middleware configuration
# TODO: Restrict origins in production to Vercel domain
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all for development
    allow_credentials=True,
    allow_methods=["*"],
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


# Placeholder endpoints (will be implemented in Phase 2)
@app.get("/api/v1/anomalies")
async def list_anomalies(
    status: str = Query(default="flagged", description="Filter by status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    List anomalies with pagination (Phase 2 implementation).
    
    Args:
        status: Filter by anomaly status
        limit: Maximum number of anomalies to return
        offset: Number of anomalies to skip
        db: Database session
    
    Returns:
        Paginated anomaly list
    """
    # Placeholder - will be implemented in Phase 2
    return {
        "items": [],
        "total": 0
    }


@app.post("/api/v1/detect")
async def trigger_detection(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Manually trigger anomaly detection (Phase 2 implementation).
    
    Args:
        db: Database session
    
    Returns:
        Detection results summary
    """
    # Placeholder - will be implemented in Phase 2
    return {
        "processed": 0,
        "new_anomalies": 0,
        "last_processed_id": 0
    }


@app.get("/api/v1/stats")
async def get_stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Get dashboard statistics (Phase 2 implementation).
    
    Args:
        db: Database session
    
    Returns:
        Dashboard statistics
    """
    # Get basic stats
    total_transactions = db.query(Transaction).count()
    
    # Get last ingestion time
    last_transaction = db.query(Transaction).order_by(
        Transaction.created_at.desc()
    ).first()
    
    last_ingestion_at = None
    if last_transaction and last_transaction.created_at:
        last_ingestion_at = last_transaction.created_at.isoformat() + "Z"
    
    return {
        "total_transactions": total_transactions,
        "total_anomalies": 0,  # Phase 2
        "flag_rate_percent": 0.0,  # Phase 2
        "top_anomalous_vendor": None,  # Phase 2
        "last_ingestion_at": last_ingestion_at,
        "model_version": "isolation_forest_v1"
    }
