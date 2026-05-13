"""
Transaction ingestion pipeline with scheduled polling.

Polls Plaid API every 120 seconds for new transactions and stores them in the database.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from database.models import SessionLocal, Transaction
from ingestion.plaid_client import plaid_client

# Configure logging
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def ingest_transactions(db: Session | None = None) -> int:
    """
    Ingest transactions from Plaid API for the last 7 days.
    
    Implements idempotent ingestion using plaid_transaction_id as deduplication key.
    
    Args:
        db: SQLAlchemy session (creates new if None)
    
    Returns:
        Count of newly inserted transactions
    """
    # Create session if not provided
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True
    
    try:
        # Calculate 7-day sliding window
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        logger.info(
            f"Starting ingestion for date range: {start_date} to {end_date}"
        )
        
        # Fetch transactions from Plaid
        try:
            transactions = plaid_client.get_transactions(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
        except ValueError as e:
            logger.error(f"Plaid client not configured: {e}")
            return 0
        except Exception as e:
            logger.error(f"Failed to fetch transactions from Plaid: {e}")
            return 0
        
        # Process each transaction
        new_count = 0
        for txn_data in transactions:
            # Check if transaction already exists (idempotency)
            existing = db.query(Transaction).filter(
                Transaction.plaid_transaction_id == txn_data["transaction_id"]
            ).first()
            
            if existing:
                # Skip duplicate
                continue
            
            # Normalize data
            normalized_amount = float(txn_data["amount"])
            normalized_date = txn_data["date"]  # Already YYYY-MM-DD
            normalized_merchant = txn_data.get("merchant_name")
            
            if normalized_merchant:
                # Strip whitespace and title-case
                normalized_merchant = normalized_merchant.strip().title()
            
            # Create new transaction record
            new_transaction = Transaction(
                plaid_transaction_id=txn_data["transaction_id"],
                account_id=txn_data.get("account_id"),
                amount=normalized_amount,
                date=normalized_date,
                merchant_name=normalized_merchant,
                category=txn_data.get("category"),
            )
            
            db.add(new_transaction)
            new_count += 1
        
        # Commit all new transactions
        if new_count > 0:
            db.commit()
            logger.info(f"Ingested {new_count} new transactions")
        else:
            logger.info("No new transactions to ingest")
        
        return new_count
    
    except Exception as e:
        logger.error(f"Error during transaction ingestion: {e}")
        db.rollback()
        return 0
    
    finally:
        if close_session:
            db.close()


def scheduled_ingestion() -> None:
    """
    Scheduled job wrapper for transaction ingestion.
    
    Called by APScheduler every 120 seconds.
    """
    logger.info("Running scheduled transaction ingestion")
    try:
        count = ingest_transactions()
        logger.info(f"Scheduled ingestion complete: {count} new transactions")
    except Exception as e:
        logger.error(f"Scheduled ingestion failed: {e}")


def start_ingestion() -> None:
    """
    Initialize and start the ingestion scheduler.
    
    Schedules transaction polling every 120 seconds.
    """
    if scheduler.running:
        logger.warning("Scheduler already running")
        return
    
    # Add scheduled job
    scheduler.add_job(
        scheduled_ingestion,
        trigger="interval",
        seconds=120,
        id="transaction_ingestion",
        name="Transaction Ingestion from Plaid",
        replace_existing=True
    )
    
    # Start scheduler
    scheduler.start()
    logger.info("Ingestion scheduler started (120-second interval)")
    
    # Run initial ingestion immediately
    logger.info("Running initial ingestion")
    scheduled_ingestion()


def stop_ingestion() -> None:
    """
    Gracefully shutdown the ingestion scheduler.
    
    Waits for any running jobs to complete before shutting down.
    """
    if not scheduler.running:
        logger.warning("Scheduler not running")
        return
    
    logger.info("Shutting down ingestion scheduler")
    scheduler.shutdown(wait=True)
    logger.info("Ingestion scheduler stopped")
