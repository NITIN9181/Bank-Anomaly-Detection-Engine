"""
Duplicate transaction detection.

Identifies potential duplicate charges within 24-hour windows.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from sqlalchemy.orm import Session

from database.models import Transaction


def detect_duplicate(
    transaction: Transaction,
    db: Session
) -> dict[str, Any] | None:
    """
    Detect duplicate transactions within 24-hour window.
    
    A transaction is considered a duplicate if another transaction exists with:
    - Same amount
    - Same merchant name
    - Same date
    - Different transaction ID
    - Within 24 hours of creation time
    
    Args:
        transaction: Transaction to check for duplicates
        db: Database session
    
    Returns:
        Dictionary with anomaly type if duplicate found, None otherwise
        Format: {"type": "duplicate", "z_score": None}
    """
    # Skip if transaction has no merchant name
    if not transaction.merchant_name:
        return None
    
    # Calculate 24-hour window
    if transaction.created_at:
        time_lower = transaction.created_at - timedelta(hours=24)
        time_upper = transaction.created_at + timedelta(hours=24)
    else:
        # If no timestamp, can't check time window
        return None
    
    # Query for potential duplicates
    duplicate = db.query(Transaction).filter(
        Transaction.amount == transaction.amount,
        Transaction.merchant_name == transaction.merchant_name,
        Transaction.date == transaction.date,
        Transaction.id != transaction.id,
        Transaction.created_at >= time_lower,
        Transaction.created_at <= time_upper
    ).first()
    
    if duplicate:
        return {
            "type": "duplicate",
            "z_score": None
        }
    
    return None
