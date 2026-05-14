"""
Inject realistic test transactions with subtle anomalies for demo purposes.

This script adds synthetic transactions that mimic real banking patterns.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from database.models import SessionLocal, Transaction
from features.engineer import update_vendor_profiles


# Realistic merchant patterns with typical spending ranges
MERCHANT_PATTERNS = {
    # Coffee shops
    "Starbucks": {"category": "Food and Drink", "range": (4.50, 12.00), "frequency": "high"},
    "Dunkin'": {"category": "Food and Drink", "range": (3.00, 8.50), "frequency": "high"},
    
    # Restaurants
    "Chipotle": {"category": "Food and Drink", "range": (10.00, 18.00), "frequency": "medium"},
    "Panera Bread": {"category": "Food and Drink", "range": (8.00, 15.00), "frequency": "medium"},
    "Olive Garden": {"category": "Food and Drink", "range": (35.00, 75.00), "frequency": "low"},
    
    # Groceries
    "Whole Foods": {"category": "Groceries", "range": (25.00, 120.00), "frequency": "medium"},
    "Trader Joe's": {"category": "Groceries", "range": (30.00, 85.00), "frequency": "medium"},
    "Walmart": {"category": "Groceries", "range": (40.00, 150.00), "frequency": "medium"},
    
    # Transportation
    "Uber": {"category": "Transportation", "range": (8.00, 28.00), "frequency": "high"},
    "Lyft": {"category": "Transportation", "range": (7.00, 25.00), "frequency": "medium"},
    "Shell Gas Station": {"category": "Transportation", "range": (35.00, 65.00), "frequency": "medium"},
    
    # Shopping
    "Amazon": {"category": "Shopping", "range": (15.00, 120.00), "frequency": "high"},
    "Target": {"category": "Shopping", "range": (25.00, 95.00), "frequency": "medium"},
    "Best Buy": {"category": "Electronics", "range": (50.00, 350.00), "frequency": "low"},
    
    # Subscriptions
    "Netflix": {"category": "Entertainment", "range": (15.99, 15.99), "frequency": "monthly"},
    "Spotify": {"category": "Entertainment", "range": (10.99, 10.99), "frequency": "monthly"},
    "Amazon Prime": {"category": "Shopping", "range": (14.99, 14.99), "frequency": "monthly"},
    "Adobe Creative Cloud": {"category": "Software", "range": (54.99, 54.99), "frequency": "monthly"},
    
    # Utilities
    "AT&T": {"category": "Utilities", "range": (75.00, 95.00), "frequency": "monthly"},
    "PG&E": {"category": "Utilities", "range": (85.00, 150.00), "frequency": "monthly"},
    
    # Fitness
    "Planet Fitness": {"category": "Health", "range": (10.00, 22.99), "frequency": "monthly"},
    "LA Fitness": {"category": "Health", "range": (29.99, 44.99), "frequency": "monthly"},
}


def get_transaction_count(frequency: str) -> int:
    """Get number of transactions based on frequency."""
    counts = {
        "high": random.randint(15, 25),
        "medium": random.randint(8, 15),
        "low": random.randint(3, 7),
        "monthly": 3,  # 3 months of history
    }
    return counts.get(frequency, 10)


def inject_test_data():
    """Inject realistic test transactions with subtle anomalies."""
    db = SessionLocal()
    
    try:
        print("🔧 Injecting realistic transaction data...")
        
        # Get current date
        today = datetime.now().date()
        
        # Generate normal transactions for each merchant
        print("\n📊 Creating realistic transaction history (90 days)...")
        normal_count = 0
        
        for merchant, pattern in MERCHANT_PATTERNS.items():
            count = get_transaction_count(pattern["frequency"])
            min_amt, max_amt = pattern["range"]
            
            for i in range(count):
                # Distribute transactions over 90 days
                if pattern["frequency"] == "monthly":
                    # Monthly subscriptions on specific days
                    days_ago = 30 * i + random.randint(1, 5)
                else:
                    days_ago = random.randint(1, 90)
                
                # Add small variance to amounts (±10%)
                variance = random.uniform(0.9, 1.1)
                amount = round(random.uniform(min_amt, max_amt) * variance, 2)
                
                txn = Transaction(
                    plaid_transaction_id=f"test_{merchant.replace(' ', '_').lower()}_{i}",
                    amount=amount,
                    date=(today - timedelta(days=days_ago)).isoformat(),
                    merchant_name=merchant,
                    category=pattern["category"],
                    created_at=datetime.utcnow()
                )
                db.add(txn)
                normal_count += 1
        
        print(f"✅ Created {normal_count} normal transactions across {len(MERCHANT_PATTERNS)} merchants")
        
        # Now inject subtle, realistic anomalies
        print("\n🚨 Injecting realistic anomalies...")
        
        # ANOMALY 1: Unusual Starbucks charge (catering order)
        print("🚨 ANOMALY 1: Starbucks $287.50 (catering order - normally $4-$12)")
        txn = Transaction(
            plaid_transaction_id="anomaly_starbucks_catering",
            amount=287.50,
            date=(today - timedelta(days=2)).isoformat(),
            merchant_name="Starbucks",
            category="Food and Drink",
            created_at=datetime.utcnow()
        )
        db.add(txn)
        
        # ANOMALY 2: Duplicate Uber charge (double billing)
        print("🚨 ANOMALY 2: Duplicate Uber charges $18.75 (double billing)")
        for i in range(2):
            txn = Transaction(
                plaid_transaction_id=f"anomaly_uber_duplicate_{i}",
                amount=18.75,
                date=(today - timedelta(days=1)).isoformat(),
                merchant_name="Uber",
                category="Transportation",
                created_at=datetime.utcnow()
            )
            db.add(txn)
        
        # ANOMALY 3: Unusual Amazon charge (expensive electronics)
        print("🚨 ANOMALY 3: Amazon $1,249.99 (laptop - normally $15-$120)")
        txn = Transaction(
            plaid_transaction_id="anomaly_amazon_laptop",
            amount=1249.99,
            date=(today - timedelta(days=3)).isoformat(),
            merchant_name="Amazon",
            category="Shopping",
            created_at=datetime.utcnow()
        )
        db.add(txn)
        
        # ANOMALY 4: Unusual Best Buy charge (way above normal)
        print("🚨 ANOMALY 4: Best Buy $2,899.00 (TV - normally $50-$350)")
        txn = Transaction(
            plaid_transaction_id="anomaly_bestbuy_tv",
            amount=2899.00,
            date=(today - timedelta(days=5)).isoformat(),
            merchant_name="Best Buy",
            category="Electronics",
            created_at=datetime.utcnow()
        )
        db.add(txn)
        
        # ANOMALY 5: Unusual gas station charge (possible skimming)
        print("🚨 ANOMALY 5: Shell Gas Station $250.00 (possible fraud - normally $35-$65)")
        txn = Transaction(
            plaid_transaction_id="anomaly_shell_fraud",
            amount=250.00,
            date=today.isoformat(),
            merchant_name="Shell Gas Station",
            category="Transportation",
            created_at=datetime.utcnow()
        )
        db.add(txn)
        
        # ANOMALY 6: Unusual Whole Foods charge (party shopping)
        print("🚨 ANOMALY 6: Whole Foods $385.00 (party shopping - normally $25-$120)")
        txn = Transaction(
            plaid_transaction_id="anomaly_wholefoods_party",
            amount=385.00,
            date=(today - timedelta(days=4)).isoformat(),
            merchant_name="Whole Foods",
            category="Groceries",
            created_at=datetime.utcnow()
        )
        db.add(txn)
        
        # Commit all transactions
        db.commit()
        anomaly_count = 7  # 6 unique anomalies + 1 duplicate = 7 transactions
        print(f"\n✅ Injected {normal_count + anomaly_count} total transactions")
        print(f"   - {normal_count} normal transactions")
        print(f"   - {anomaly_count} anomalous transactions")
        
        # Update vendor profiles
        print("\n🔄 Updating vendor profiles with new data...")
        update_vendor_profiles(db)
        print("✅ Vendor profiles updated")
        
        # Show summary
        total_txns = db.query(Transaction).count()
        print(f"\n📈 Total transactions in database: {total_txns}")
        print("\n🎯 Now run detection to see the anomalies!")
        print("   - Click 'Run Detection' in the dashboard")
        print("   - Or run: curl -X POST http://localhost:8000/api/v1/detect")
        print("\n💡 Expected anomalies:")
        print("   1. Starbucks $287.50 (catering)")
        print("   2. Duplicate Uber $18.75")
        print("   3. Amazon $1,249.99 (laptop)")
        print("   4. Best Buy $2,899.00 (TV)")
        print("   5. Shell Gas $250.00 (fraud)")
        print("   6. Whole Foods $385.00 (party)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    inject_test_data()
