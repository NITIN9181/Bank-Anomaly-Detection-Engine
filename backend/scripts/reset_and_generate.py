"""
Reset database and generate multi-account dataset.

Run from backend directory: python -m scripts.reset_and_generate
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Account, AccountLink, Anomaly, SessionLocal, Transaction, User, VendorProfile, create_tables


def clear_all_data():
    """Clear all existing data from database."""
    db = SessionLocal()
    
    try:
        print("🗑️  Clearing existing data...")
        
        # First, ensure all tables exist
        print("   Creating tables if they don't exist...")
        create_tables()
        
        # Delete in order (foreign key constraints)
        anomaly_count = db.query(Anomaly).delete()
        vendor_count = db.query(VendorProfile).delete()
        txn_count = db.query(Transaction).delete()
        link_count = db.query(AccountLink).delete()
        account_count = db.query(Account).delete()
        user_count = db.query(User).delete()
        
        db.commit()
        
        print(f"✅ Cleared:")
        print(f"   - {user_count} users")
        print(f"   - {account_count} accounts")
        print(f"   - {link_count} account links")
        print(f"   - {txn_count} transactions")
        print(f"   - {anomaly_count} anomalies")
        print(f"   - {vendor_count} vendor profiles")
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    # Clear old data
    clear_all_data()
    
    # Generate new multi-account data
    print("\n" + "="*60)
    from scripts.generate_advanced_data import generate_multi_account_data
    generate_multi_account_data(days=90)
