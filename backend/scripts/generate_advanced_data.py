"""
Multi-Account Synthetic Data Generator with User Personas.

Generates realistic multi-account banking data with:
- 3 distinct user personas (salary worker, freelancer, business)
- Account relationships (family, business, suspicious)
- Realistic spending patterns per persona
- Cross-account fraud ring patterns
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from database.models import Account, AccountLink, SessionLocal, Transaction, User
from features.engineer import update_vendor_profiles


# ============================================================================
# USER PERSONAS
# ============================================================================

PERSONAS = [
    {
        "user_id": "user_sarah_001",
        "name": "Sarah Chen",
        "risk_profile": "low",
        "typical_monthly_spend": 3500.0,
        "payroll_day": 15,
        "account_type": "checking",
        "spending_pattern": "predictable",
        "merchants": [
            ("Whole Foods", "Groceries", 80, 150, 25),  # Increased frequency
            ("Shell Gas Station", "Transportation", 40, 60, 12),
            ("Starbucks", "Food and Drink", 5, 12, 45),
            ("Netflix", "Entertainment", 15.99, 15.99, 1),
            ("AT&T", "Utilities", 85, 95, 1),
            ("Planet Fitness", "Health", 22.99, 22.99, 1),
            ("Target", "Shopping", 30, 120, 15),
            ("CVS Pharmacy", "Health", 15, 50, 8),
            ("Panera Bread", "Food and Drink", 10, 18, 12),
            ("Spotify", "Entertainment", 9.99, 9.99, 1),
        ],
    },
    {
        "user_id": "user_mike_002",
        "name": "Mike Rodriguez",
        "risk_profile": "medium",
        "typical_monthly_spend": 6000.0,
        "payroll_day": None,  # Irregular freelancer income
        "account_type": "checking",
        "spending_pattern": "spikey",
        "merchants": [
            ("Amazon", "Shopping", 20, 200, 35),
            ("Starbucks", "Food and Drink", 5, 15, 50),
            ("Uber", "Transportation", 10, 30, 40),
            ("Adobe Creative Cloud", "Software", 54.99, 54.99, 1),
            ("Dropbox", "Software", 11.99, 11.99, 1),
            ("Chipotle", "Food and Drink", 12, 18, 25),
            ("Best Buy", "Electronics", 100, 500, 5),
            ("DoorDash", "Food and Drink", 15, 35, 30),
            ("Shell Gas Station", "Transportation", 40, 60, 10),
            ("Walgreens", "Health", 10, 40, 8),
        ],
    },
    {
        "user_id": "user_corp_003",
        "name": "TechStart LLC",
        "risk_profile": "high",
        "typical_monthly_spend": 25000.0,
        "payroll_day": 1,
        "account_type": "business",
        "spending_pattern": "complex",
        "merchants": [
            ("Amazon", "Shopping", 50, 5000, 60),  # AWS bills - increased
            ("Comcast", "Utilities", 129.99, 129.99, 1),
            ("AT&T", "Utilities", 250, 350, 1),
            ("Whole Foods", "Groceries", 100, 300, 20),
            ("Uber", "Transportation", 15, 50, 80),
            ("Adobe Creative Cloud", "Software", 54.99, 54.99, 10),
            ("Slack", "Software", 12.50, 12.50, 25),
            ("GitHub", "Software", 21.00, 21.00, 10),
            ("Zoom", "Software", 14.99, 14.99, 10),
            ("Office Depot", "Office Supplies", 50, 300, 15),
        ],
    },
    {
        "user_id": "user_emily_004",
        "name": "Emily Watson",
        "risk_profile": "low",
        "typical_monthly_spend": 2800.0,
        "payroll_day": 1,
        "account_type": "checking",
        "spending_pattern": "predictable",
        "merchants": [
            ("Trader Joe's", "Groceries", 60, 120, 20),
            ("Chevron", "Transportation", 35, 55, 10),
            ("Starbucks", "Food and Drink", 5, 12, 35),
            ("Hulu", "Entertainment", 12.99, 12.99, 1),
            ("Verizon", "Utilities", 75, 85, 1),
            ("LA Fitness", "Health", 29.99, 29.99, 1),
            ("Walmart", "Shopping", 25, 100, 18),
            ("Rite Aid", "Health", 12, 45, 6),
            ("Subway", "Food and Drink", 8, 14, 15),
        ],
    },
    {
        "user_id": "user_david_005",
        "name": "David Kim",
        "risk_profile": "medium",
        "typical_monthly_spend": 4500.0,
        "payroll_day": 15,
        "account_type": "checking",
        "spending_pattern": "spikey",
        "merchants": [
            ("Amazon", "Shopping", 25, 180, 30),
            ("Costco", "Groceries", 100, 250, 8),
            ("Shell Gas Station", "Transportation", 40, 65, 12),
            ("Netflix", "Entertainment", 15.99, 15.99, 1),
            ("T-Mobile", "Utilities", 90, 100, 1),
            ("Chipotle", "Food and Drink", 12, 18, 20),
            ("Home Depot", "Home Improvement", 50, 300, 6),
            ("Uber Eats", "Food and Drink", 18, 40, 25),
            ("Apple Store", "Electronics", 50, 400, 4),
        ],
    },
]


# ============================================================================
# TRANSACTION GENERATION
# ============================================================================

def generate_transactions_for_persona(
    persona: dict[str, Any],
    account_id: int,
    days: int = 90
) -> list[Transaction]:
    """
    Generate realistic transactions for a user persona.
    
    Args:
        persona: User persona configuration
        account_id: Database account ID
        days: Number of days to generate
    
    Returns:
        List of Transaction objects
    """
    transactions = []
    today = datetime.now().date()
    
    for merchant, category, min_amt, max_amt, freq_per_month in persona["merchants"]:
        # Calculate total transactions for the period
        total_txns = int((freq_per_month / 30) * days)
        
        # Adjust based on spending pattern
        if persona["spending_pattern"] == "predictable":
            # Evenly distributed
            variance = 0.1
        elif persona["spending_pattern"] == "spikey":
            # More variance, some days with multiple txns
            variance = 0.3
            total_txns = int(total_txns * random.uniform(0.8, 1.5))
        else:  # complex
            # High variance, power-law distribution
            variance = 0.5
            total_txns = int(total_txns * random.uniform(0.7, 2.0))
        
        for _ in range(total_txns):
            # Generate date
            days_ago = random.randint(1, days)
            txn_date = today - timedelta(days=days_ago)
            
            # Generate amount with variance
            if min_amt == max_amt:  # Fixed subscription
                amount = min_amt
            else:
                mean = (min_amt + max_amt) / 2
                std = (max_amt - min_amt) / 6
                amount = np.random.normal(mean, std)
                amount = max(min_amt, min(max_amt, amount))
                amount *= random.uniform(1 - variance, 1 + variance)
            
            transactions.append(Transaction(
                plaid_transaction_id=f"multi_acc_{account_id}_{merchant.replace(' ', '_')}_{_}_{random.randint(1000, 9999)}",
                account_id=account_id,
                amount=round(amount, 2),
                date=txn_date.isoformat(),
                merchant_name=merchant,
                category=category,
                created_at=datetime.utcnow()
            ))
    
    return transactions


# ============================================================================
# FRAUD RING GENERATION
# ============================================================================

def generate_fraud_ring_transactions(
    account_ids: list[int],
    days: int = 90
) -> list[Transaction]:
    """
    Generate coordinated fraud ring transactions.
    
    Pattern: Multiple accounts hit same merchant within 5-minute window.
    
    Args:
        account_ids: List of account IDs in the ring
        days: Number of days to generate
    
    Returns:
        List of Transaction objects
    """
    transactions = []
    today = datetime.now().date()
    
    # Generate 8-12 fraud ring events (increased)
    for event_num in range(random.randint(8, 12)):
        # Pick a random date
        days_ago = random.randint(1, days)
        event_date = today - timedelta(days=days_ago)
        
        # Pick a high-value merchant
        merchant = random.choice(["Amazon", "Best Buy", "Apple Store", "Newegg", "B&H Photo"])
        
        # All accounts hit within 5 minutes
        base_hour = random.randint(2, 5)  # Late night (suspicious)
        
        for i, acc_id in enumerate(account_ids):
            amount = random.uniform(800, 2500)
            
            transactions.append(Transaction(
                plaid_transaction_id=f"fraud_ring_{event_num}_{acc_id}_{random.randint(1000, 9999)}",
                account_id=acc_id,
                amount=round(amount, 2),
                date=event_date.isoformat(),
                merchant_name=merchant,
                category="Electronics" if merchant != "Amazon" else "Shopping",
                created_at=datetime.utcnow()
            ))
    
    return transactions


def generate_anomalous_transactions(
    account_id: int,
    days: int = 90
) -> list[Transaction]:
    """
    Generate various types of anomalous transactions.
    
    Includes:
    - Velocity anomalies (burst spending)
    - Amount anomalies (unusually high)
    - Duplicate transactions
    - Geographic anomalies (unusual merchants)
    
    Args:
        account_id: Database account ID
        days: Number of days to generate
    
    Returns:
        List of anomalous Transaction objects
    """
    transactions = []
    today = datetime.now().date()
    
    # Velocity anomaly: 5 transactions in 1 hour
    velocity_date = today - timedelta(days=random.randint(10, 30))
    for i in range(5):
        transactions.append(Transaction(
            plaid_transaction_id=f"velocity_{account_id}_{i}_{random.randint(1000, 9999)}",
            account_id=account_id,
            amount=round(random.uniform(150, 400), 2),
            date=velocity_date.isoformat(),
            merchant_name=random.choice(["Amazon", "Target", "Walmart"]),
            category="Shopping",
            created_at=datetime.utcnow()
        ))
    
    # Amount anomaly: Unusually high transaction
    amount_date = today - timedelta(days=random.randint(5, 20))
    transactions.append(Transaction(
        plaid_transaction_id=f"high_amount_{account_id}_{random.randint(1000, 9999)}",
        account_id=account_id,
        amount=round(random.uniform(5000, 8500), 2),
        date=amount_date.isoformat(),
        merchant_name="Luxury Retailer",
        category="Shopping",
        created_at=datetime.utcnow()
    ))
    
    # Duplicate transactions
    dup_date = today - timedelta(days=random.randint(15, 40))
    dup_amount = round(random.uniform(75, 150), 2)
    dup_merchant = random.choice(["Shell Gas Station", "Starbucks", "Chipotle"])
    for i in range(2):
        transactions.append(Transaction(
            plaid_transaction_id=f"duplicate_{account_id}_{i}_{random.randint(1000, 9999)}",
            account_id=account_id,
            amount=dup_amount,
            date=dup_date.isoformat(),
            merchant_name=dup_merchant,
            category="Food and Drink",
            created_at=datetime.utcnow()
        ))
    
    # Geographic anomaly: Unusual merchant
    geo_date = today - timedelta(days=random.randint(25, 50))
    transactions.append(Transaction(
        plaid_transaction_id=f"geographic_{account_id}_{random.randint(1000, 9999)}",
        account_id=account_id,
        amount=round(random.uniform(200, 600), 2),
        date=geo_date.isoformat(),
        merchant_name="International Merchant XYZ",
        category="Travel",
        created_at=datetime.utcnow()
    ))
    
    return transactions


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_multi_account_data(days: int = 90) -> None:
    """
    Generate multi-account synthetic dataset with fraud rings.
    
    Args:
        days: Number of days of transaction history to generate
    """
    db = SessionLocal()
    
    try:
        print("🚀 Multi-Account Data Generator")
        print("=" * 60)
        print(f"Generating {days}-day multi-account dataset...")
        print()
        
        # Step 1: Create users and accounts
        print("👥 Creating user personas and accounts...")
        users_created = []
        accounts_created = []
        
        for persona in PERSONAS:
            # Create user
            user = User(
                user_id=persona["user_id"],
                name=persona["name"],
                risk_profile=persona["risk_profile"],
                typical_monthly_spend=persona["typical_monthly_spend"],
                payroll_day=persona["payroll_day"],
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.flush()  # Get user.id
            users_created.append(user)
            
            # Create primary account
            account = Account(
                account_id=f"acc_{persona['user_id'].split('_')[-1]}",
                user_id=user.id,
                account_type=persona["account_type"],
                balance=random.uniform(1000, 10000),
                created_at=datetime.utcnow()
            )
            db.add(account)
            db.flush()  # Get account.id
            accounts_created.append(account)
            
            print(f"   ✅ {user.name} ({user.risk_profile} risk, ${user.typical_monthly_spend:,.0f}/mo)")
        
        # Create additional business sub-account for Corp LLC
        corp_user = users_created[2]  # TechStart LLC
        corp_sub_account = Account(
            account_id="acc_003_payroll",
            user_id=corp_user.id,
            account_type="business",
            balance=random.uniform(50000, 100000),
            created_at=datetime.utcnow()
        )
        db.add(corp_sub_account)
        db.flush()
        accounts_created.append(corp_sub_account)
        print(f"   ✅ TechStart LLC Payroll Account (business sub-account)")
        
        db.commit()
        
        # Step 2: Create account links
        print("\n🔗 Creating account relationships...")
        
        # Sarah and Mike are family (high strength)
        family_link = AccountLink(
            account_a_id=accounts_created[0].id,  # Sarah
            account_b_id=accounts_created[1].id,  # Mike
            link_type="family",
            strength=0.9,
            detected_at=datetime.utcnow()
        )
        db.add(family_link)
        print(f"   ✅ Family link: Sarah ↔ Mike (strength=0.9)")
        
        # Corp LLC main and payroll accounts (business link)
        business_link = AccountLink(
            account_a_id=accounts_created[2].id,  # Corp main
            account_b_id=accounts_created[3].id,  # Corp payroll
            link_type="business",
            strength=1.0,
            detected_at=datetime.utcnow()
        )
        db.add(business_link)
        print(f"   ✅ Business link: TechStart Main ↔ Payroll (strength=1.0)")
        
        # Create 2 suspicious accounts for fraud ring
        fraud_accounts = []
        for i in range(2):
            fraud_user = User(
                user_id=f"user_fraud_{i+1:03d}",
                name=f"Suspicious Account {i+1}",
                risk_profile="high",
                typical_monthly_spend=0.0,
                payroll_day=None,
                created_at=datetime.utcnow()
            )
            db.add(fraud_user)
            db.flush()
            
            fraud_account = Account(
                account_id=f"acc_fraud_{i+1:03d}",
                user_id=fraud_user.id,
                account_type="checking",
                balance=random.uniform(100, 500),
                created_at=datetime.utcnow()
            )
            db.add(fraud_account)
            db.flush()
            fraud_accounts.append(fraud_account)
        
        # Suspicious shared_ip link between fraud accounts
        fraud_link = AccountLink(
            account_a_id=fraud_accounts[0].id,
            account_b_id=fraud_accounts[1].id,
            link_type="shared_ip",
            strength=0.3,
            detected_at=datetime.utcnow()
        )
        db.add(fraud_link)
        print(f"   ✅ Suspicious link: Fraud Account 1 ↔ 2 (shared_ip, strength=0.3)")
        
        db.commit()
        
        # Step 3: Generate normal transactions
        print("\n📊 Generating normal transactions...")
        all_transactions = []
        
        for i, persona in enumerate(PERSONAS):
            account = accounts_created[i]
            txns = generate_transactions_for_persona(persona, account.id, days)
            all_transactions.extend(txns)
            print(f"   ✅ {persona['name']}: {len(txns)} transactions")
        
        # Step 4: Generate anomalous transactions for each account
        print("\n⚠️  Injecting anomalous transactions...")
        for i, persona in enumerate(PERSONAS):
            account = accounts_created[i]
            anomaly_txns = generate_anomalous_transactions(account.id, days)
            all_transactions.extend(anomaly_txns)
            print(f"   ✅ {persona['name']}: {len(anomaly_txns)} anomalies injected")
        
        # Step 5: Generate fraud ring transactions
        print("\n🚨 Generating fraud ring transactions...")
        fraud_ring_txns = generate_fraud_ring_transactions(
            [fa.id for fa in fraud_accounts],
            days
        )
        all_transactions.extend(fraud_ring_txns)
        print(f"   ✅ Fraud ring: {len(fraud_ring_txns)} coordinated transactions")
        
        # Step 6: Insert all transactions
        print("\n💾 Inserting transactions into database...")
        for txn in all_transactions:
            db.add(txn)
        
        db.commit()
        print(f"   ✅ Inserted {len(all_transactions)} transactions")
        
        # Step 7: Update vendor profiles
        print("\n🔄 Computing vendor profiles...")
        update_vendor_profiles(db)
        print("   ✅ Vendor profiles updated")
        
        # Summary
        total_anomalies = len(fraud_ring_txns) + (len(PERSONAS) * 9)  # 9 anomalies per persona
        print("\n" + "=" * 60)
        print("✨ Multi-Account Dataset Generation Complete!")
        print("=" * 60)
        print(f"\n📊 Dataset Statistics:")
        print(f"   Users: {len(users_created) + len(fraud_accounts)}")
        print(f"   Accounts: {len(accounts_created) + len(fraud_accounts)}")
        print(f"   Account Links: 3 (1 family, 1 business, 1 suspicious)")
        print(f"   Transactions: {len(all_transactions)}")
        print(f"   Anomalies Injected: ~{total_anomalies}")
        print(f"   Date Range: {days} days")
        print(f"\n🎯 User Personas:")
        for persona in PERSONAS:
            print(f"   - {persona['name']}: {persona['risk_profile']} risk, ${persona['typical_monthly_spend']:,.0f}/mo")
        print(f"\n🚨 Fraud Ring:")
        print(f"   - 2 suspicious accounts with shared_ip link")
        print(f"   - {len(fraud_ring_txns)} coordinated high-value transactions")
        print(f"\n⚠️  Anomaly Types Injected:")
        print(f"   - Velocity anomalies (burst spending)")
        print(f"   - Amount anomalies (unusually high)")
        print(f"   - Duplicate transactions")
        print(f"   - Geographic anomalies (unusual merchants)")
        print(f"   - Fraud ring patterns (coordinated)")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Run fraud ring detection: curl -X GET http://localhost:8000/api/v1/rings")
        print(f"   2. View accounts: curl -X GET http://localhost:8000/api/v1/accounts")
        print(f"   3. Run normal detection: curl -X POST http://localhost:8000/api/v1/detect")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    generate_multi_account_data(days=90)
