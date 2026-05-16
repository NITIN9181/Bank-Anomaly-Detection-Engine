"""
Flooding Attack: "Hide in Noise"

Floods system with legitimate transactions to bury fraudulent ones.
Tests if ML can maintain precision/recall under high noise conditions.
"""

from __future__ import annotations

import random
from typing import Any

import numpy as np
from sqlalchemy.orm import Session

from database.models import Anomaly
from detection.orchestrator import run_detection
from features.engineer import update_vendor_profiles
from tests.adversarial.base import AdversarialTest, calculate_metrics, create_test_transaction


class FloodingAttack(AdversarialTest):
    """
    Hide in Noise attack: bury anomalies in legitimate traffic.
    
    Simulates fraudster flooding system with normal-looking transactions
    to reduce detection probability.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "flooding_attack"
        self.description = "Flood system with noise to hide anomalies"
    
    def run(self, db: Session) -> dict[str, Any]:
        """
        Execute flooding attack test.
        
        Args:
            db: Database session
        
        Returns:
            Test results with precision/recall metrics
        """
        merchants = ["Amazon", "Target", "Walmart", "Best Buy", "Costco"]
        
        # Step 1: Generate 1000 normal transactions
        normal_txns = []
        merchant_stats = {m: [] for m in merchants}
        
        for _ in range(1000):
            merchant = random.choice(merchants)
            amount = np.random.uniform(10, 200)
            day_offset = random.randint(1, 30)
            
            txn = create_test_transaction(
                account_id=None,
                merchant=merchant,
                amount=round(amount, 2),
                date_offset_days=day_offset,
                db=db,
                category="Shopping"
            )
            normal_txns.append(txn)
            merchant_stats[merchant].append(amount)
        
        # Step 2: Embed 5 anomalous transactions (5x merchant average)
        embedded_anomalies = []
        for i in range(5):
            merchant = random.choice(merchants)
            avg_amount = np.mean(merchant_stats[merchant])
            anomalous_amount = avg_amount * 5  # 5x average
            day_offset = random.randint(1, 30)
            
            txn = create_test_transaction(
                account_id=None,
                merchant=merchant,
                amount=round(anomalous_amount, 2),
                date_offset_days=day_offset,
                db=db,
                category="Shopping"
            )
            embedded_anomalies.append(txn)
        
        db.commit()
        
        # Update vendor profiles
        update_vendor_profiles(db)
        
        # Run detection
        detected_anomalies = run_detection(db)
        
        # Analyze results
        embedded_ids = {txn.id for txn in embedded_anomalies}
        normal_ids = {txn.id for txn in normal_txns}
        detected_ids = {a.transaction_id for a in detected_anomalies}
        
        true_positives = len(embedded_ids & detected_ids)
        false_positives = len(normal_ids & detected_ids)
        false_negatives = len(embedded_ids - detected_ids)
        
        # Calculate metrics
        metrics = calculate_metrics(true_positives, false_positives, false_negatives)
        
        # Pass criteria
        passed = (
            metrics["recall"] >= 0.60 and
            metrics["precision"] >= 0.50 and
            metrics["f1_score"] >= 0.55
        )
        
        return {
            "test_name": self.name,
            "description": self.description,
            "passed": passed,
            "metrics": {
                "true_positives": true_positives,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1_score": metrics["f1_score"],
                "total_normal_transactions": len(normal_txns),
                "total_embedded_anomalies": len(embedded_anomalies)
            },
            "details": [
                f"Embedded {len(embedded_anomalies)} anomalies in {len(normal_txns)} normal transactions",
                f"Detected {true_positives}/{len(embedded_anomalies)} embedded anomalies (recall: {metrics['recall']:.1%})",
                f"False positives: {false_positives}/{len(normal_txns)} ({false_positives/len(normal_txns):.1%})",
                f"Precision: {metrics['precision']:.1%} (target: ≥50%)",
                f"F1 score: {metrics['f1_score']:.3f} (target: ≥0.55)"
            ],
            "severity": "high" if not passed else "low"
        }
