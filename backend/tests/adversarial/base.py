"""
Base classes and utilities for adversarial testing.

Provides abstract base class and helper functions for all adversarial tests.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from database.models import Anomaly, Transaction
from detection.orchestrator import run_detection


class AdversarialTest(ABC):
    """
    Abstract base class for adversarial tests.
    
    All adversarial tests must inherit from this class and implement
    the run() method.
    """
    
    def __init__(self):
        """Initialize test with name and description."""
        self.name: str = self.__class__.__name__
        self.description: str = ""
    
    @abstractmethod
    def run(self, db: Session) -> dict[str, Any]:
        """
        Execute the adversarial test.
        
        Args:
            db: Database session
        
        Returns:
            Test results dictionary with metrics and pass/fail status
        """
        pass


def create_test_transaction(
    account_id: int | None,
    merchant: str,
    amount: float,
    date_offset_days: int,
    db: Session,
    category: str = "Shopping"
) -> Transaction:
    """
    Create a test transaction with specified parameters.
    
    Args:
        account_id: Account ID (can be None for backward compat)
        merchant: Merchant name
        amount: Transaction amount
        date_offset_days: Days before now for transaction date
        db: Database session
        category: Transaction category
    
    Returns:
        Created Transaction object
    """
    now = datetime.utcnow()
    txn_date = (now - timedelta(days=date_offset_days)).date()
    
    txn = Transaction(
        plaid_transaction_id=f"adv_{uuid4().hex[:12]}",
        account_id=account_id,
        amount=amount,
        date=txn_date.isoformat(),
        merchant_name=merchant,
        category=category,
        created_at=now - timedelta(days=date_offset_days)
    )
    
    db.add(txn)
    db.flush()  # Get txn.id without committing
    
    return txn


def run_detection_on_date_range(
    start_date: str,
    end_date: str,
    db: Session
) -> list[Anomaly]:
    """
    Run detection pipeline on transactions in date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        db: Database session
    
    Returns:
        List of detected anomalies
    """
    # Run full detection pipeline
    new_anomalies = run_detection(db)
    
    # Filter to date range
    filtered_anomalies = []
    for anomaly in new_anomalies:
        txn = db.query(Transaction).get(anomaly.transaction_id)
        if txn and start_date <= txn.date <= end_date:
            filtered_anomalies.append(anomaly)
    
    return filtered_anomalies


def calculate_metrics(
    true_positives: int,
    false_positives: int,
    false_negatives: int
) -> dict[str, float]:
    """
    Calculate precision, recall, and F1 score.
    
    Args:
        true_positives: Correctly detected anomalies
        false_positives: Normal transactions incorrectly flagged
        false_negatives: Anomalies missed
    
    Returns:
        Dictionary with precision, recall, f1_score
    """
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1_score, 3)
    }
