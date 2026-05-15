"""
Clear existing data and inject advanced synthetic transactions.
"""

from __future__ import annotations

from database.models import Anomaly, SessionLocal, Transaction, VendorProfile


def clear_all_data():
    """Clear all existing transactions, anomalies, and vendor profiles."""
    db = SessionLocal()
    
    try:
        print("🗑️  Clearing existing data...")
        
        # Delete in order (foreign key constraints)
        anomaly_count = db.query(Anomaly).delete()
        vendor_count = db.query(VendorProfile).delete()
        txn_count = db.query(Transaction).delete()
        
        db.commit()
        
        print(f"✅ Cleared {txn_count} transactions, {anomaly_count} anomalies, {vendor_count} vendor profiles")
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    # Clear old data
    clear_all_data()
    
    # Inject new advanced data
    print("\n" + "="*60)
    from advanced_data_generator import generate_advanced_dataset
    generate_advanced_dataset(days=90)
