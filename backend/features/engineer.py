"""
Feature engineering for vendor profiles.

Computes rolling 6-month statistics per merchant for anomaly detection.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from database.models import SessionLocal, Transaction, VendorProfile

# Configure logging
logger = logging.getLogger(__name__)


def update_vendor_profiles(db: Session | None = None) -> None:
    """
    Update vendor profiles with rolling 6-month statistics.
    
    For each merchant:
    - Calculates mean and standard deviation of transaction amounts
    - Counts total transactions in the 6-month window
    - Updates or inserts vendor profile record
    
    Args:
        db: SQLAlchemy session (creates new if None)
    """
    # Create session if not provided
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True
    
    try:
        # Calculate 6-month window
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)  # 6 months
        
        logger.info(
            f"Updating vendor profiles for window: {start_date} to {end_date}"
        )
        
        # Fetch all transactions in 6-month window
        transactions = db.query(Transaction).filter(
            Transaction.date >= start_date.isoformat(),
            Transaction.date <= end_date.isoformat(),
            Transaction.merchant_name.isnot(None)
        ).all()
        
        if not transactions:
            logger.info("No transactions found in 6-month window")
            return
        
        # Convert to pandas DataFrame for efficient computation
        df = pd.DataFrame([
            {
                "merchant_name": txn.merchant_name,
                "amount": txn.amount,
                "category": txn.category,
            }
            for txn in transactions
        ])
        
        # Group by merchant and compute statistics
        grouped = df.groupby("merchant_name")
        
        updated_count = 0
        for merchant_name, group in grouped:
            # Calculate statistics
            amounts = group["amount"]
            mean_amount = float(amounts.mean())
            std_amount = float(amounts.std())
            count = len(group)
            
            # Handle std=0 case (all transactions same amount)
            if pd.isna(std_amount) or std_amount == 0.0:
                std_amount = 1.0  # Avoid division by zero in z-score calculation
            
            # Get most common category
            category = group["category"].mode()[0] if not group["category"].isna().all() else None
            
            # Check if profile exists
            existing_profile = db.query(VendorProfile).filter(
                VendorProfile.merchant_name == merchant_name
            ).first()
            
            if existing_profile:
                # Update existing profile
                existing_profile.avg_amount = mean_amount
                existing_profile.std_amount = std_amount
                existing_profile.transaction_count = count
                existing_profile.category = category
                existing_profile.last_updated = datetime.utcnow()
            else:
                # Create new profile
                new_profile = VendorProfile(
                    merchant_name=merchant_name,
                    category=category,
                    avg_amount=mean_amount,
                    std_amount=std_amount,
                    transaction_count=count,
                    last_updated=datetime.utcnow()
                )
                db.add(new_profile)
            
            updated_count += 1
        
        # Commit all updates
        db.commit()
        logger.info(f"Updated {updated_count} vendor profiles")
    
    except Exception as e:
        logger.error(f"Error updating vendor profiles: {e}")
        db.rollback()
        raise
    
    finally:
        if close_session:
            db.close()


def get_vendor_profile(merchant_name: str, db: Session) -> VendorProfile | None:
    """
    Retrieve vendor profile for a specific merchant.
    
    Args:
        merchant_name: Merchant name to look up
        db: SQLAlchemy session
    
    Returns:
        VendorProfile object or None if not found
    """
    return db.query(VendorProfile).filter(
        VendorProfile.merchant_name == merchant_name
    ).first()
