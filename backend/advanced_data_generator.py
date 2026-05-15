"""
Advanced Synthetic Transaction Generator

Generates realistic banking data with:
- User personas with spending habits
- Temporal patterns (weekday/weekend, time-of-day)
- Seasonal trends (holidays, month-end)
- Geographic patterns
- Merchant loyalty and frequency
- Complex anomaly types (account takeover, card testing, etc.)
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from database.models import SessionLocal, Transaction
from features.engineer import update_vendor_profiles


# ============================================================================
# USER PERSONAS
# ============================================================================

class UserPersona:
    """Represents a user's spending behavior profile."""
    
    def __init__(
        self,
        name: str,
        income_bracket: str,
        spending_style: str,
        preferred_categories: list[str],
        risk_tolerance: float,
    ):
        self.name = name
        self.income_bracket = income_bracket  # low, medium, high
        self.spending_style = spending_style  # frugal, moderate, lavish
        self.preferred_categories = preferred_categories
        self.risk_tolerance = risk_tolerance  # 0.0 to 1.0


PERSONAS = [
    UserPersona(
        name="Budget-Conscious Student",
        income_bracket="low",
        spending_style="frugal",
        preferred_categories=["Food and Drink", "Transportation", "Groceries"],
        risk_tolerance=0.2,
    ),
    UserPersona(
        name="Young Professional",
        income_bracket="medium",
        spending_style="moderate",
        preferred_categories=["Food and Drink", "Shopping", "Entertainment", "Transportation"],
        risk_tolerance=0.5,
    ),
    UserPersona(
        name="Affluent Executive",
        income_bracket="high",
        spending_style="lavish",
        preferred_categories=["Shopping", "Travel", "Food and Drink", "Entertainment"],
        risk_tolerance=0.8,
    ),
]


# ============================================================================
# MERCHANT DATABASE WITH REALISTIC PATTERNS
# ============================================================================

MERCHANT_DATABASE = {
    # Coffee & Quick Service (high frequency, low amount)
    "Starbucks": {
        "category": "Food and Drink",
        "base_range": (4.50, 12.00),
        "frequency": "daily",
        "peak_hours": [7, 8, 9, 14, 15],  # Morning and afternoon
        "weekend_multiplier": 0.7,
        "loyalty_discount": 0.9,
    },
    "Dunkin'": {
        "category": "Food and Drink",
        "base_range": (3.00, 8.50),
        "frequency": "daily",
        "peak_hours": [6, 7, 8, 9],
        "weekend_multiplier": 0.6,
        "loyalty_discount": 0.85,
    },
    
    # Fast Casual (medium frequency, medium amount)
    "Chipotle": {
        "category": "Food and Drink",
        "base_range": (10.00, 18.00),
        "frequency": "weekly",
        "peak_hours": [12, 13, 18, 19],
        "weekend_multiplier": 1.2,
        "loyalty_discount": 1.0,
    },
    "Panera Bread": {
        "category": "Food and Drink",
        "base_range": (8.00, 15.00),
        "frequency": "weekly",
        "peak_hours": [12, 13, 14],
        "weekend_multiplier": 0.9,
        "loyalty_discount": 0.95,
    },
    
    # Sit-Down Restaurants (low frequency, high amount)
    "Olive Garden": {
        "category": "Food and Drink",
        "base_range": (35.00, 75.00),
        "frequency": "monthly",
        "peak_hours": [18, 19, 20],
        "weekend_multiplier": 1.5,
        "loyalty_discount": 1.0,
    },
    "The Cheesecake Factory": {
        "category": "Food and Drink",
        "base_range": (45.00, 95.00),
        "frequency": "monthly",
        "peak_hours": [18, 19, 20, 21],
        "weekend_multiplier": 1.6,
        "loyalty_discount": 1.0,
    },
    
    # Groceries (weekly, variable)
    "Whole Foods": {
        "category": "Groceries",
        "base_range": (25.00, 120.00),
        "frequency": "weekly",
        "peak_hours": [17, 18, 19],
        "weekend_multiplier": 1.3,
        "loyalty_discount": 1.0,
    },
    "Trader Joe's": {
        "category": "Groceries",
        "base_range": (30.00, 85.00),
        "frequency": "weekly",
        "peak_hours": [17, 18, 19, 20],
        "weekend_multiplier": 1.4,
        "loyalty_discount": 1.0,
    },
    "Walmart": {
        "category": "Groceries",
        "base_range": (40.00, 150.00),
        "frequency": "biweekly",
        "peak_hours": [10, 11, 15, 16, 17],
        "weekend_multiplier": 1.5,
        "loyalty_discount": 1.0,
    },
    "Costco": {
        "category": "Groceries",
        "base_range": (80.00, 250.00),
        "frequency": "monthly",
        "peak_hours": [10, 11, 14, 15],
        "weekend_multiplier": 1.8,
        "loyalty_discount": 1.0,
    },
    
    # Transportation (variable frequency)
    "Uber": {
        "category": "Transportation",
        "base_range": (8.00, 28.00),
        "frequency": "weekly",
        "peak_hours": [7, 8, 17, 18, 22, 23],
        "weekend_multiplier": 1.4,
        "loyalty_discount": 1.0,
    },
    "Lyft": {
        "category": "Transportation",
        "base_range": (7.00, 25.00),
        "frequency": "weekly",
        "peak_hours": [7, 8, 17, 18, 22, 23],
        "weekend_multiplier": 1.3,
        "loyalty_discount": 1.0,
    },
    "Shell Gas Station": {
        "category": "Transportation",
        "base_range": (35.00, 65.00),
        "frequency": "weekly",
        "peak_hours": [7, 8, 17, 18],
        "weekend_multiplier": 1.1,
        "loyalty_discount": 0.95,
    },
    "Chevron": {
        "category": "Transportation",
        "base_range": (38.00, 70.00),
        "frequency": "weekly",
        "peak_hours": [7, 8, 17, 18],
        "weekend_multiplier": 1.1,
        "loyalty_discount": 0.95,
    },
    
    # E-commerce (high frequency, variable)
    "Amazon": {
        "category": "Shopping",
        "base_range": (15.00, 120.00),
        "frequency": "weekly",
        "peak_hours": [20, 21, 22],  # Evening browsing
        "weekend_multiplier": 1.2,
        "loyalty_discount": 1.0,
    },
    "Target": {
        "category": "Shopping",
        "base_range": (25.00, 95.00),
        "frequency": "biweekly",
        "peak_hours": [14, 15, 16, 17],
        "weekend_multiplier": 1.4,
        "loyalty_discount": 1.0,
    },
    
    # Electronics (low frequency, high amount)
    "Best Buy": {
        "category": "Electronics",
        "base_range": (50.00, 350.00),
        "frequency": "quarterly",
        "peak_hours": [14, 15, 16, 17],
        "weekend_multiplier": 1.5,
        "loyalty_discount": 1.0,
    },
    "Apple Store": {
        "category": "Electronics",
        "base_range": (100.00, 1200.00),
        "frequency": "yearly",
        "peak_hours": [14, 15, 16],
        "weekend_multiplier": 1.3,
        "loyalty_discount": 1.0,
    },
    
    # Subscriptions (monthly, fixed)
    "Netflix": {
        "category": "Entertainment",
        "base_range": (15.99, 15.99),
        "frequency": "monthly",
        "peak_hours": [0],  # Midnight auto-charge
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    "Spotify": {
        "category": "Entertainment",
        "base_range": (10.99, 10.99),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    "Amazon Prime": {
        "category": "Shopping",
        "base_range": (14.99, 14.99),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    "Adobe Creative Cloud": {
        "category": "Software",
        "base_range": (54.99, 54.99),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    "Dropbox": {
        "category": "Software",
        "base_range": (11.99, 11.99),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    
    # Utilities (monthly, variable)
    "AT&T": {
        "category": "Utilities",
        "base_range": (75.00, 95.00),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    "PG&E": {
        "category": "Utilities",
        "base_range": (85.00, 150.00),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    "Comcast": {
        "category": "Utilities",
        "base_range": (89.99, 129.99),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    
    # Fitness (monthly, fixed)
    "Planet Fitness": {
        "category": "Health",
        "base_range": (10.00, 22.99),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    "LA Fitness": {
        "category": "Health",
        "base_range": (29.99, 44.99),
        "frequency": "monthly",
        "peak_hours": [0],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
    
    # Entertainment (variable)
    "AMC Theatres": {
        "category": "Entertainment",
        "base_range": (12.00, 35.00),
        "frequency": "monthly",
        "peak_hours": [18, 19, 20, 21],
        "weekend_multiplier": 1.8,
        "loyalty_discount": 0.9,
    },
    "Ticketmaster": {
        "category": "Entertainment",
        "base_range": (50.00, 250.00),
        "frequency": "quarterly",
        "peak_hours": [20, 21, 22],
        "weekend_multiplier": 1.0,
        "loyalty_discount": 1.0,
    },
}


# ============================================================================
# TEMPORAL PATTERNS
# ============================================================================

def is_weekend(date: datetime) -> bool:
    """Check if date is weekend."""
    return date.weekday() >= 5


def is_holiday(date: datetime) -> bool:
    """Check if date is a major holiday."""
    holidays = [
        (1, 1),   # New Year
        (2, 14),  # Valentine's
        (7, 4),   # July 4th
        (10, 31), # Halloween
        (11, 24), # Thanksgiving (approx)
        (12, 25), # Christmas
    ]
    return (date.month, date.day) in holidays


def is_month_end(date: datetime) -> bool:
    """Check if date is near month end (bill payment time)."""
    return date.day >= 28


def get_time_of_day_multiplier(hour: int, peak_hours: list[int]) -> float:
    """Get spending multiplier based on time of day."""
    if hour in peak_hours:
        return 1.2
    elif abs(hour - min(peak_hours, key=lambda x: abs(x - hour))) <= 1:
        return 1.0
    else:
        return 0.3


# ============================================================================
# TRANSACTION GENERATOR
# ============================================================================

def generate_transaction_amount(
    merchant: str,
    merchant_data: dict[str, Any],
    date: datetime,
    is_loyal_customer: bool = False,
) -> float:
    """Generate realistic transaction amount with temporal patterns."""
    min_amt, max_amt = merchant_data["base_range"]
    
    # Base amount with normal distribution
    mean = (min_amt + max_amt) / 2
    std = (max_amt - min_amt) / 6  # 99.7% within range
    amount = np.random.normal(mean, std)
    amount = max(min_amt, min(max_amt, amount))  # Clamp to range
    
    # Apply weekend multiplier
    if is_weekend(date):
        amount *= merchant_data["weekend_multiplier"]
    
    # Apply holiday multiplier
    if is_holiday(date):
        amount *= 1.3
    
    # Apply loyalty discount
    if is_loyal_customer:
        amount *= merchant_data["loyalty_discount"]
    
    # Add random variance (±10%)
    amount *= random.uniform(0.9, 1.1)
    
    return round(amount, 2)


def get_transaction_frequency(frequency: str) -> int:
    """Convert frequency string to number of transactions per 90 days."""
    frequencies = {
        "daily": random.randint(60, 90),
        "weekly": random.randint(10, 15),
        "biweekly": random.randint(5, 8),
        "monthly": random.randint(2, 4),
        "quarterly": random.randint(1, 2),
        "yearly": 1,
    }
    return frequencies.get(frequency, 5)


def generate_normal_transactions(days: int = 90) -> list[dict[str, Any]]:
    """Generate realistic normal transactions over specified days."""
    transactions = []
    today = datetime.now().date()
    
    # Select a persona
    persona = random.choice(PERSONAS)
    
    for merchant, merchant_data in MERCHANT_DATABASE.items():
        # Skip if not in persona's preferred categories
        if merchant_data["category"] not in persona.preferred_categories:
            if random.random() > 0.3:  # 30% chance to use anyway
                continue
        
        # Determine if loyal customer (affects frequency and discounts)
        is_loyal = random.random() < 0.4
        
        # Get transaction count
        count = get_transaction_frequency(merchant_data["frequency"])
        
        # Adjust count based on persona spending style
        if persona.spending_style == "frugal":
            count = int(count * 0.7)
        elif persona.spending_style == "lavish":
            count = int(count * 1.3)
        
        for _ in range(count):
            # Generate random date within window
            days_ago = random.randint(1, days)
            txn_date = today - timedelta(days=days_ago)
            
            # Generate random hour (weighted by peak hours)
            if random.random() < 0.6:  # 60% during peak hours
                hour = random.choice(merchant_data["peak_hours"])
            else:
                hour = random.randint(0, 23)
            
            # Generate amount
            amount = generate_transaction_amount(
                merchant, merchant_data, txn_date, is_loyal
            )
            
            transactions.append({
                "merchant_name": merchant,
                "category": merchant_data["category"],
                "amount": amount,
                "date": txn_date,
                "hour": hour,
            })
    
    return transactions


# ============================================================================
# ANOMALY GENERATORS
# ============================================================================

def generate_account_takeover_anomaly(today: datetime.date) -> list[dict[str, Any]]:
    """
    Account Takeover: Sudden burst of high-value transactions in short time.
    Pattern: Multiple expensive purchases within 1-2 hours.
    """
    anomalies = []
    takeover_date = today - timedelta(days=random.randint(1, 3))
    takeover_hour = random.randint(2, 5)  # Late night (suspicious)
    
    # Burst of 3-5 high-value transactions
    for i in range(random.randint(3, 5)):
        merchant = random.choice(["Best Buy", "Apple Store", "Amazon"])
        amount = random.uniform(800, 2500)
        
        anomalies.append({
            "merchant_name": merchant,
            "category": MERCHANT_DATABASE[merchant]["category"],
            "amount": round(amount, 2),
            "date": takeover_date,
            "hour": takeover_hour,
            "anomaly_type": "account_takeover",
        })
        takeover_hour += random.randint(0, 1)  # Within 1-2 hours
    
    return anomalies


def generate_card_testing_anomaly(today: datetime.date) -> list[dict[str, Any]]:
    """
    Card Testing: Multiple small transactions to test stolen card.
    Pattern: 5-10 small charges ($1-$5) in rapid succession.
    """
    anomalies = []
    test_date = today - timedelta(days=random.randint(1, 5))
    test_hour = random.randint(1, 4)
    
    # Multiple small test charges
    for i in range(random.randint(5, 10)):
        merchant = random.choice(["Amazon", "Target", "Walmart"])
        amount = random.uniform(0.99, 4.99)
        
        anomalies.append({
            "merchant_name": merchant,
            "category": MERCHANT_DATABASE[merchant]["category"],
            "amount": round(amount, 2),
            "date": test_date,
            "hour": test_hour,
            "anomaly_type": "card_testing",
        })
    
    return anomalies


def generate_geographic_anomaly(today: datetime.date) -> list[dict[str, Any]]:
    """
    Geographic Anomaly: Transactions in impossible locations.
    Pattern: Two transactions far apart within short time.
    """
    anomalies = []
    anomaly_date = today - timedelta(days=random.randint(1, 7))
    
    # Transaction 1: Local (e.g., Starbucks in SF)
    anomalies.append({
        "merchant_name": "Starbucks",
        "category": "Food and Drink",
        "amount": 6.50,
        "date": anomaly_date,
        "hour": 8,
        "anomaly_type": "geographic",
    })
    
    # Transaction 2: Impossible location 30 minutes later (e.g., Best Buy in NYC)
    anomalies.append({
        "merchant_name": "Best Buy",
        "category": "Electronics",
        "amount": 450.00,
        "date": anomaly_date,
        "hour": 8,  # Same hour (impossible to travel)
        "anomaly_type": "geographic",
    })
    
    return anomalies


def generate_velocity_anomaly(today: datetime.date) -> list[dict[str, Any]]:
    """
    Velocity Anomaly: Unusually high transaction frequency.
    Pattern: 15+ transactions in a single day (normal is 2-5).
    """
    anomalies = []
    anomaly_date = today - timedelta(days=random.randint(1, 5))
    
    merchants = list(MERCHANT_DATABASE.keys())
    for _ in range(random.randint(15, 25)):
        merchant = random.choice(merchants)
        merchant_data = MERCHANT_DATABASE[merchant]
        min_amt, max_amt = merchant_data["base_range"]
        amount = random.uniform(min_amt, max_amt)
        
        anomalies.append({
            "merchant_name": merchant,
            "category": merchant_data["category"],
            "amount": round(amount, 2),
            "date": anomaly_date,
            "hour": random.randint(6, 23),
            "anomaly_type": "velocity",
        })
    
    return anomalies


def generate_volumetric_anomalies(today: datetime.date) -> list[dict[str, Any]]:
    """
    Volumetric Anomalies: Unusually large charges for specific merchants.
    Pattern: Single transaction way above normal range.
    """
    anomalies = []
    
    # Starbucks catering order
    anomalies.append({
        "merchant_name": "Starbucks",
        "category": "Food and Drink",
        "amount": 287.50,
        "date": today - timedelta(days=2),
        "hour": 10,
        "anomaly_type": "volumetric",
    })
    
    # Amazon expensive electronics
    anomalies.append({
        "merchant_name": "Amazon",
        "category": "Shopping",
        "amount": 1249.99,
        "date": today - timedelta(days=3),
        "hour": 21,
        "anomaly_type": "volumetric",
    })
    
    # Best Buy TV purchase
    anomalies.append({
        "merchant_name": "Best Buy",
        "category": "Electronics",
        "amount": 2899.00,
        "date": today - timedelta(days=5),
        "hour": 15,
        "anomaly_type": "volumetric",
    })
    
    # Shell gas station (possible skimming)
    anomalies.append({
        "merchant_name": "Shell Gas Station",
        "category": "Transportation",
        "amount": 250.00,
        "date": today,
        "hour": 3,  # Late night (suspicious)
        "anomaly_type": "volumetric",
    })
    
    # Whole Foods party shopping
    anomalies.append({
        "merchant_name": "Whole Foods",
        "category": "Groceries",
        "amount": 385.00,
        "date": today - timedelta(days=4),
        "hour": 17,
        "anomaly_type": "volumetric",
    })
    
    return anomalies


def generate_duplicate_anomaly(today: datetime.date) -> list[dict[str, Any]]:
    """
    Duplicate Anomaly: Same merchant and amount within short time.
    Pattern: Double billing or processing error.
    """
    anomalies = []
    anomaly_date = today - timedelta(days=1)
    amount = 18.75
    
    for _ in range(2):
        anomalies.append({
            "merchant_name": "Uber",
            "category": "Transportation",
            "amount": amount,
            "date": anomaly_date,
            "hour": 18,
            "anomaly_type": "duplicate",
        })
    
    return anomalies


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_advanced_dataset(days: int = 90) -> None:
    """Generate advanced synthetic dataset with complex patterns."""
    db = SessionLocal()
    
    try:
        print("🚀 Advanced Synthetic Data Generator")
        print("=" * 60)
        print(f"Generating {days}-day transaction history with complex patterns...")
        print()
        
        # Generate normal transactions
        print("📊 Generating normal transactions...")
        normal_txns = generate_normal_transactions(days)
        print(f"   ✅ Generated {len(normal_txns)} normal transactions")
        
        # Generate anomalies
        print("\n🚨 Generating complex anomalies...")
        today = datetime.now().date()
        
        anomalies = []
        anomalies.extend(generate_account_takeover_anomaly(today))
        print(f"   ✅ Account Takeover: {len(generate_account_takeover_anomaly(today))} transactions")
        
        anomalies.extend(generate_card_testing_anomaly(today))
        print(f"   ✅ Card Testing: {len(generate_card_testing_anomaly(today))} transactions")
        
        anomalies.extend(generate_geographic_anomaly(today))
        print(f"   ✅ Geographic Anomaly: {len(generate_geographic_anomaly(today))} transactions")
        
        anomalies.extend(generate_velocity_anomaly(today))
        print(f"   ✅ Velocity Anomaly: {len(generate_velocity_anomaly(today))} transactions")
        
        anomalies.extend(generate_volumetric_anomalies(today))
        print(f"   ✅ Volumetric Anomalies: {len(generate_volumetric_anomalies(today))} transactions")
        
        anomalies.extend(generate_duplicate_anomaly(today))
        print(f"   ✅ Duplicate Anomaly: {len(generate_duplicate_anomaly(today))} transactions")
        
        # Combine all transactions
        all_txns = normal_txns + anomalies
        print(f"\n📈 Total transactions: {len(all_txns)}")
        print(f"   - Normal: {len(normal_txns)}")
        print(f"   - Anomalous: {len(anomalies)}")
        
        # Insert into database
        print("\n💾 Inserting into database...")
        for i, txn in enumerate(all_txns):
            db_txn = Transaction(
                plaid_transaction_id=f"advanced_txn_{i}",
                amount=txn["amount"],
                date=txn["date"].isoformat(),
                merchant_name=txn["merchant_name"],
                category=txn["category"],
                created_at=datetime.utcnow()
            )
            db.add(db_txn)
        
        db.commit()
        print("   ✅ Database insertion complete")
        
        # Update vendor profiles
        print("\n🔄 Computing vendor profiles...")
        update_vendor_profiles(db)
        print("   ✅ Vendor profiles updated")
        
        # Summary
        print("\n" + "=" * 60)
        print("✨ Advanced Dataset Generation Complete!")
        print("=" * 60)
        print(f"\n📊 Dataset Statistics:")
        print(f"   Total Transactions: {len(all_txns)}")
        print(f"   Unique Merchants: {len(MERCHANT_DATABASE)}")
        print(f"   Date Range: {days} days")
        print(f"   Anomaly Types: 6 (account takeover, card testing, geographic, velocity, volumetric, duplicate)")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Run detection: curl -X POST http://localhost:8000/api/v1/detect")
        print(f"   2. View dashboard: http://localhost:3000")
        print(f"   3. Expect {len(anomalies)} anomalies to be flagged")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    generate_advanced_dataset(days=90)
