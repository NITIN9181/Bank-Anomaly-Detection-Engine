"""
Evasion Attack: "Boiling the Frog"

Gradually increases transaction amounts over time to evade statistical detection.
Tests if system can detect slow drift in spending patterns.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

import numpy as np
from sqlalchemy.orm import Session

from database.models import Anomaly, Transaction
from detection.orchestrator import run_detection
from features.engineer import update_vendor_profiles
from tests.adversarial.base import AdversarialTest, create_test_transaction


class EvasionAttack(AdversarialTest):
    """
    Boiling the Frog attack: gradual amount increase.
    
    Simulates fraudster slowly increasing transaction amounts over weeks
    to avoid triggering static thresholds.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "evasion_attack"
        self.description = "Gradual amount increase to evade statistical detection"
    
    def run(self, db: Session) -> dict[str, Any]:
        """
        Execute evasion attack test.
        
        Args:
            db: Database session
        
        Returns:
            Test results with metrics
        """
        merchant = "Amazon"
        
        # Phase 1: Baseline (days 1-10) - mean=$100, std=$15
        baseline_txns = []
        for day in range(30, 20, -1):  # 30 days ago to 21 days ago
            amount = np.random.normal(100, 15)
            amount = max(70, min(130, amount))  # Clamp to reasonable range
            
            txn = create_test_transaction(
                account_id=None,
                merchant=merchant,
                amount=round(amount, 2),
                date_offset_days=day,
                db=db,
                category="Shopping"
            )
            baseline_txns.append(txn)
        
        # Phase 2: Gradual increase (days 11-20) - mean=$130, std=$15
        transition_txns = []
        for day in range(20, 10, -1):  # 20 days ago to 11 days ago
            amount = np.random.normal(130, 15)
            amount = max(100, min(160, amount))
            
            txn = create_test_transaction(
                account_id=None,
                merchant=merchant,
                amount=round(amount, 2),
                date_offset_days=day,
                db=db,
                category="Shopping"
            )
            transition_txns.append(txn)
        
        # Phase 3: Attack (days 21-30) - mean=$170, std=$20
        attack_txns = []
        for day in range(10, 0, -1):  # 10 days ago to today
            amount = np.random.normal(170, 20)
            amount = max(130, min(210, amount))
            
            txn = create_test_transaction(
                account_id=None,
                merchant=merchant,
                amount=round(amount, 2),
                date_offset_days=day,
                db=db,
                category="Shopping"
            )
            attack_txns.append(txn)
        
        db.commit()
        
        # Update vendor profiles
        update_vendor_profiles(db)
        
        # Run detection
        anomalies = run_detection(db)
        
        # Analyze results
        baseline_anomalies = [
            a for a in anomalies
            if a.transaction_id in [t.id for t in baseline_txns]
        ]
        
        attack_anomalies = [
            a for a in anomalies
            if a.transaction_id in [t.id for t in attack_txns]
        ]
        
        # Calculate metrics
        baseline_false_positives = len(baseline_anomalies)
        attack_detection_rate = len(attack_anomalies) / len(attack_txns)
        
        # Find first detection day in attack phase
        days_to_detection = None
        if attack_anomalies:
            first_anomaly_txn = db.query(Transaction).get(attack_anomalies[0].transaction_id)
            if first_anomaly_txn:
                days_ago = (datetime.utcnow().date() - datetime.fromisoformat(first_anomaly_txn.date).date()).days
                days_to_detection = 30 - days_ago  # Convert to "day number" in test
        
        # Pass criteria
        passed = (
            baseline_false_positives <= 2 and
            attack_detection_rate >= 0.30 and
            (days_to_detection is None or days_to_detection <= 25)
        )
        
        return {
            "test_name": self.name,
            "description": self.description,
            "passed": passed,
            "metrics": {
                "baseline_false_positives": baseline_false_positives,
                "attack_detection_rate": round(attack_detection_rate, 3),
                "anomalies_detected_in_attack": len(attack_anomalies),
                "total_attack_transactions": len(attack_txns),
                "days_to_detection": days_to_detection,
                "false_negative_rate": round(1 - attack_detection_rate, 3)
            },
            "details": [
                f"Baseline phase: {baseline_false_positives} false positives (target: ≤2)",
                f"Attack phase: {len(attack_anomalies)}/{len(attack_txns)} detected (target: ≥3)",
                f"Detection rate: {attack_detection_rate:.1%} (target: ≥30%)",
                f"Days to detection: {days_to_detection if days_to_detection else 'N/A'} (target: ≤25)"
            ],
            "severity": "high" if not passed else "low"
        }
