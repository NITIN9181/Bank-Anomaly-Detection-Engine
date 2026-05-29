"""
Orchestrator for multi-layer anomaly detection pipeline.

Coordinates statistical, ML, and duplicate detection layers.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from database.models import Anomaly, Transaction, VendorProfile
from detection.duplicate import detect_duplicate
from detection.isolation_forest import load_or_train_model, predict_anomaly_score
from detection.statistical import detect_statistical_anomaly

# Configure logging
logger = logging.getLogger(__name__)


def run_detection(db: Session) -> list[Anomaly]:
    """
    Run multi-layer anomaly detection on all unprocessed transactions.
    
    Dual-layer detection: statistical for clear deviations, ML for subtle patterns.
    
    Detection layers:
    1. Statistical (Z-score): Flags transactions >3 std deviations from vendor baseline
    2. ML (Isolation Forest): Detects structural anomalies in transaction patterns
    3. Duplicate: Identifies potential duplicate charges within 24-hour windows
    
    Args:
        db: Database session
    
    Returns:
        List of newly created Anomaly objects
    """
    logger.info("Starting anomaly detection pipeline")
    
    # Dual-layer detection: statistical for clear deviations, ML for subtle patterns.
    
    # Step 1: Load or train Isolation Forest model
    try:
        model, encoder = load_or_train_model(db)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load/train model: {e}")
        # Continue with statistical and duplicate detection only
        model = None
        encoder = None
    
    # Step 2: Get all merchant names for encoding
    merchant_results = db.query(Transaction.merchant_name).distinct().all()
    all_merchants = [m[0] for m in merchant_results if m[0] is not None]
    logger.info(f"Found {len(all_merchants)} unique merchants")
    
    # Step 3: Find unprocessed transactions (not in anomalies table)
    from sqlalchemy import select
    processed_ids = select(Anomaly.transaction_id)
    unprocessed = db.query(Transaction).filter(
        ~Transaction.id.in_(processed_ids)
    ).all()
    
    logger.info(f"Found {len(unprocessed)} unprocessed transactions")
    
    if not unprocessed:
        logger.info("No unprocessed transactions to analyze")
        return []
    # Step 4: Process each transaction through detection layers
    new_anomalies = []
    
    for txn in unprocessed:
        # Get vendor profile for statistical detection
        profile = None
        if txn.merchant_name:
            profile = db.query(VendorProfile).filter(
                VendorProfile.merchant_name == txn.merchant_name
            ).first()
        
        # Layer 1: Statistical detection
        stat_result = detect_statistical_anomaly(txn, profile)
        
        # Layer 2: ML detection (Isolation Forest)
        ml_result = None
        if model is not None and encoder is not None:
            try:
                score = predict_anomaly_score(txn, model, encoder, db)
                # Threshold: scores < -0.15 are considered anomalous
                if score < -0.15:
                    ml_result = {
                        "type": "deviant_pattern",
                        "isolation_score": round(score, 4)
                    }
            except Exception as e:
                logger.warning(f"ML detection failed for transaction {txn.id}: {e}")
        
        # Layer 3: Duplicate detection
        dup_result = detect_duplicate(txn, db)
        
        # Create anomaly if any layer flagged the transaction
        if stat_result or ml_result or dup_result:
            # Determine primary anomaly type (first non-None result)
            anomaly_type = None
            if stat_result:
                anomaly_type = stat_result["type"]
            elif ml_result:
                anomaly_type = ml_result["type"]
            elif dup_result:
                anomaly_type = dup_result["type"]
            
            # Extract scores
            z_score = stat_result.get("z_score") if stat_result else None
            isolation_score = ml_result.get("isolation_score") if ml_result else None
            
            # Create anomaly record
            anomaly = Anomaly(
                transaction_id=txn.id,
                anomaly_type=anomaly_type,
                z_score=z_score,
                isolation_score=isolation_score,
                status="flagged"
            )
            
            db.add(anomaly)
            new_anomalies.append(anomaly)
            
            logger.info(
                f"Flagged transaction {txn.id} as {anomaly_type} "
                f"(z={z_score}, iso={isolation_score})"
            )
    
    # Step 5: Commit all anomalies
    if new_anomalies:
        db.commit()
        logger.info(f"Created {len(new_anomalies)} new anomaly records")
    else:
        logger.info("No anomalies detected")
    
    # Step 6: Check if model should be retrained
    # (Optional for now - log warning if many new transactions)
    total_transactions = db.query(Transaction).count()
    if total_transactions > 50 and model is not None:
        # Could implement incremental retraining logic here
        logger.info(f"Model trained on {total_transactions} transactions")
    
    return new_anomalies


def get_anomalies_since(db: Session, hours: int = 24) -> list[Anomaly]:
    """
    Retrieve anomalies detected within the last N hours.
    
    Args:
        db: Database session
        hours: Number of hours to look back
    
    Returns:
        List of Anomaly objects
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    anomalies = db.query(Anomaly).filter(
        Anomaly.detected_at >= cutoff_time
    ).all()
    
    return anomalies
