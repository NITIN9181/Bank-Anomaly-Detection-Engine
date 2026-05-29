"""
Isolation Forest anomaly detection for structural pattern recognition.

Detects subtle anomalies that statistical methods miss using unsupervised ML.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sqlalchemy.orm import Session

from database.models import Transaction

# Configure logging
logger = logging.getLogger(__name__)

# Model persistence paths
MODEL_DIR = Path("data")
MODEL_PATH = MODEL_DIR / "isolation_forest.pkl"
ENCODER_PATH = MODEL_DIR / "merchant_encoder.pkl"


def extract_features(
    transaction: Transaction,
    encoder: LabelEncoder,
    db: Session
) -> np.ndarray:
    """
    Extract feature vector for Isolation Forest prediction.
    
    Features:
    - amount: Transaction dollar amount
    - hour_of_day: Hour when transaction occurred (0-23)
    - day_of_week: Day of week (0=Monday, 6=Sunday)
    - days_since_last_txn: Days since previous transaction from same merchant
    - merchant_encoded: Integer-encoded merchant name
    
    Args:
        transaction: Transaction to extract features from
        encoder: Fitted LabelEncoder for merchant names
        db: Database session for querying previous transactions
    
    Returns:
        Feature vector as numpy array of shape (5,)
    """
    # Feature 1: Amount
    amount = float(transaction.amount)
    
    # Feature 2: Hour of day (0-23)
    hour_of_day = transaction.created_at.hour if transaction.created_at else 0
    
    # Feature 3: Day of week (0=Monday, 6=Sunday)
    day_of_week = transaction.created_at.weekday() if transaction.created_at else 0
    
    # Feature 4: Days since last transaction from same merchant
    days_since_last_txn = 0.0
    if transaction.merchant_name:
        # Query previous transaction from same merchant
        previous_txn = db.query(Transaction).filter(
            Transaction.merchant_name == transaction.merchant_name,
            Transaction.id < transaction.id
        ).order_by(Transaction.created_at.desc()).first()
        
        if previous_txn and previous_txn.created_at and transaction.created_at:
            delta = transaction.created_at - previous_txn.created_at
            days_since_last_txn = delta.total_seconds() / 86400.0  # Convert to days
    
    # Feature 5: Merchant encoded as integer
    merchant_encoded = 0
    if transaction.merchant_name:
        try:
            merchant_encoded = encoder.transform([transaction.merchant_name])[0]
        except ValueError:
            # Unknown merchant not in training set - use 0 as default
            merchant_encoded = 0
    
    return np.array([
        amount,
        hour_of_day,
        day_of_week,
        days_since_last_txn,
        merchant_encoded
    ])


def train_isolation_forest(
    transactions: list[Transaction],
    db: Session
) -> tuple[IsolationForest, LabelEncoder]:
    """
    Train Isolation Forest model on transaction features.
    
    Isolation Forest: unsupervised ML for structural anomalies. No labeled fraud data needed.
    
    Args:
        transactions: List of transactions to train on
        db: Database session for feature extraction
    
    Returns:
        Tuple of (trained model, fitted label encoder)
    """
    logger.info(f"Training Isolation Forest on {len(transactions)} transactions")
    
    if not transactions:
        raise ValueError("Cannot train Isolation Forest: no transactions provided")
    
    # Extract all unique merchant names for encoding
    all_merchants = list(set(
        txn.merchant_name for txn in transactions if txn.merchant_name
    ))
    
    # Fit label encoder
    encoder = LabelEncoder()
    encoder.fit(all_merchants)
    
    # Extract features for all transactions
    feature_matrix = []
    for txn in transactions:
        features = extract_features(txn, encoder, db)
        feature_matrix.append(features)
    
    feature_matrix = np.array(feature_matrix)
    logger.info(f"Feature matrix shape: {feature_matrix.shape}")
    
    # Isolation Forest: unsupervised ML for structural anomalies. No labeled fraud data needed.
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        max_samples="auto",
        max_features=1.0
    )
    
    # Fit model
    model.fit(feature_matrix)
    logger.info("Isolation Forest training complete")
    
    # Ensure data directory exists
    MODEL_DIR.mkdir(exist_ok=True)
    
    # Persist model and encoder
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")
    logger.info(f"Encoder saved to {ENCODER_PATH}")
    
    return model, encoder


def load_or_train_model(db: Session) -> tuple[IsolationForest, LabelEncoder]:
    """
    Load existing model or train new one if stale/missing.
    
    Model is considered stale if older than 24 hours.
    
    Args:
        db: Database session
    
    Returns:
        Tuple of (model, encoder)
    """
    # Check if model files exist and are recent
    if MODEL_PATH.exists() and ENCODER_PATH.exists():
        # Check file age
        model_age = datetime.now() - datetime.fromtimestamp(
            os.path.getmtime(MODEL_PATH)
        )
        
        if model_age < timedelta(hours=24):
            logger.info(f"Loading existing model (age: {model_age})")
            model = joblib.load(MODEL_PATH)
            encoder = joblib.load(ENCODER_PATH)
            return model, encoder
        else:
            logger.info(f"Model is stale (age: {model_age}), retraining")
    else:
        logger.info("Model files not found, training new model")
    
    # Fetch all transactions for training
    transactions = db.query(Transaction).all()
    
    if len(transactions) < 10:
        logger.warning(f"Only {len(transactions)} transactions available for training")
    
    # Train new model
    return train_isolation_forest(transactions, db)


def predict_anomaly_score(
    transaction: Transaction,
    model: IsolationForest,
    encoder: LabelEncoder,
    db: Session
) -> float:
    """
    Predict anomaly score for a transaction.
    
    Args:
        transaction: Transaction to evaluate
        model: Trained Isolation Forest model
        encoder: Fitted LabelEncoder for merchants
        db: Database session
    
    Returns:
        Anomaly score (negative = more anomalous)
    """
    features = extract_features(transaction, encoder, db)
    score = model.decision_function([features])[0]
    return float(score)
