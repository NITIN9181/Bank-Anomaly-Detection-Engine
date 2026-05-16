"""
Velocity Attack: "Burst Spending"

Rapid succession of transactions to simulate stolen card usage.
Tests if system can detect velocity anomalies (many transactions in short time).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from database.models import Anomaly
from detection.orchestrator import run_detection
from features.engineer import update_vendor_profiles
from tests.adversarial.base import AdversarialTest, create_test_transaction


class VelocityAttack(AdversarialTest):
    """
    Burst Spending attack: rapid transaction succession.
    
    Simulates stolen card being used rapidly before owner notices.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "velocity_attack"
        self.description = "Rapid burst of transactions to test velocity detection"
    
    def run(self, db: Session) -> dict[str, Any]:
        """
        Execute velocity attack test.
        
        Args:
            db: Database session
        
        Returns:
            Test results with velocity detection metrics
        """
        merchant = "Steam"
        
        # Step 1: Establish normal pattern (1 transaction per 3 days)
        normal_txns = []
        for i in range(10):
            day_offset = 30 - (i * 3)  # Every 3 days
            amount = 20.0 + (i * 4)  # $20-$60 range
            
            txn = create_test_transaction(
                account_id=None,
                merchant=merchant,
                amount=amount,
                date_offset_days=day_offset,
                db=db,
                category="Entertainment"
            )
            normal_txns.append(txn)
        
        # Step 2: Create burst attack (20 transactions within 60 minutes)
        # All transactions on same day (today), but with slightly different timestamps
        burst_txns = []
        base_time = datetime.utcnow()
        
        for i in range(20):
            # Create transaction with timestamp spread over 60 minutes
            minutes_offset = i * 3  # 3 minutes apart
            txn_time = base_time - timedelta(minutes=minutes_offset)
            
            amount = 50.0 + (i * 2.5)  # $50-$100 range
            
            txn = create_test_transaction(
                account_id=None,
                merchant=merchant,
                amount=amount,
                date_offset_days=0,  # Today
                db=db,
                category="Entertainment"
            )
            
            # Adjust created_at to simulate burst timing
            txn.created_at = txn_time
            
            burst_txns.append(txn)
        
        db.commit()
        
        # Update vendor profiles
        update_vendor_profiles(db)
        
        # Run detection
        anomalies = run_detection(db)
        
        # Analyze results
        burst_ids = {txn.id for txn in burst_txns}
        burst_anomalies = [
            a for a in anomalies
            if a.transaction_id in burst_ids
        ]
        
        # Calculate metrics
        total_burst_amount = sum(txn.amount for txn in burst_txns)
        velocity_anomalies_detected = len(burst_anomalies)
        
        # Check if any anomaly is classified as velocity/deviant pattern
        velocity_classified = any(
            "velocity" in a.anomaly_type.lower() or
            "deviant" in a.anomaly_type.lower() or
            "pattern" in a.anomaly_type.lower()
            for a in burst_anomalies
        )
        
        # Pass criteria
        passed = (
            velocity_anomalies_detected >= 1 and
            velocity_classified
        )
        
        return {
            "test_name": self.name,
            "description": self.description,
            "passed": passed,
            "metrics": {
                "burst_transactions": len(burst_txns),
                "time_window_minutes": 60,
                "velocity_anomalies_detected": velocity_anomalies_detected,
                "total_burst_amount": round(total_burst_amount, 2),
                "detection_rate": round(velocity_anomalies_detected / len(burst_txns), 3),
                "velocity_classified": velocity_classified
            },
            "details": [
                f"Created {len(burst_txns)} transactions within 60 minutes",
                f"Total burst amount: ${total_burst_amount:.2f}",
                f"Anomalies detected: {velocity_anomalies_detected}/{len(burst_txns)}",
                f"Velocity-specific classification: {velocity_classified}",
                f"Detection rate: {velocity_anomalies_detected/len(burst_txns):.1%}",
                "✓ System detected velocity anomaly" if passed else "⚠️  System did NOT detect velocity pattern",
                "Recommendation: Implement time-window velocity checks" if not passed else ""
            ],
            "severity": "high" if not passed else "low"
        }
