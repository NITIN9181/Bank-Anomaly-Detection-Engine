"""
Temporal Spoofing Attack: "Backdated Transactions"

Inserts transactions with dates far in the past to manipulate balances or hide timing.
Tests if system validates temporal consistency between transaction date and ingestion time.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from database.models import Transaction
from detection.orchestrator import run_detection
from tests.adversarial.base import AdversarialTest, create_test_transaction


class TemporalSpoofingAttack(AdversarialTest):
    """
    Backdated Transactions attack.
    
    Simulates fraudster inserting old transactions to manipulate balances
    or hide timing patterns.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "temporal_spoofing"
        self.description = "Backdated transactions to evade temporal validation"
    
    def run(self, db: Session) -> dict[str, Any]:
        """
        Execute temporal spoofing attack test.
        
        Args:
            db: Database session
        
        Returns:
            Test results with temporal validation metrics
        """
        # Create a backdated transaction (90 days old date, but created now)
        backdated_txn = create_test_transaction(
            account_id=None,
            merchant="Suspicious Merchant",
            amount=500.0,
            date_offset_days=90,  # Transaction date is 90 days ago
            db=db,
            category="Shopping"
        )
        
        # Manually adjust created_at to simulate recent ingestion
        # (transaction date is old, but it was just added to system)
        backdated_txn.created_at = datetime.utcnow()
        
        db.commit()
        
        # Run detection
        anomalies = run_detection(db)
        
        # Check if backdated transaction was flagged
        backdated_anomaly = None
        for a in anomalies:
            if a.transaction_id == backdated_txn.id:
                backdated_anomaly = a
                break
        
        # Check if transaction was rejected or flagged
        rejected = False  # Current system doesn't reject
        flagged = backdated_anomaly is not None
        handled = rejected or flagged
        
        # Calculate temporal gap
        txn_date = datetime.fromisoformat(backdated_txn.date).date()
        created_date = backdated_txn.created_at.date()
        temporal_gap_days = (created_date - txn_date).days
        
        # Pass criteria: system should handle backdated transactions
        # Either by rejecting them or flagging as anomalies
        passed = handled
        
        return {
            "test_name": self.name,
            "description": self.description,
            "passed": passed,
            "metrics": {
                "backdated_transactions": 1,
                "rejected": rejected,
                "flagged": flagged,
                "handled": handled,
                "temporal_gap_days": temporal_gap_days
            },
            "details": [
                f"Created transaction with date 90 days in past",
                f"Temporal gap: {temporal_gap_days} days between transaction date and ingestion",
                f"Rejected by ingestion: {rejected}",
                f"Flagged by detection: {flagged}",
                f"Properly handled: {handled} (target: True)",
                "⚠️  Current system does NOT validate temporal consistency" if not handled else "✓ System properly handles backdated transactions",
                "Recommendation: Add temporal validation to ingestion pipeline" if not handled else ""
            ],
            "severity": "high" if not passed else "low"
        }
