# Advanced Synthetic Data Generation

## Overview

The advanced data generator creates **production-grade synthetic banking data** with realistic patterns, temporal dynamics, and complex anomaly types that go far beyond basic tutorials.

---

## 🎭 User Personas

The system models three distinct user spending profiles:

### 1. Budget-Conscious Student
- **Income**: Low
- **Spending Style**: Frugal
- **Preferred Categories**: Food & Drink, Transportation, Groceries
- **Risk Tolerance**: 20%
- **Behavior**: Frequent small purchases, avoids luxury spending

### 2. Young Professional
- **Income**: Medium
- **Spending Style**: Moderate
- **Preferred Categories**: Food & Drink, Shopping, Entertainment, Transportation
- **Risk Tolerance**: 50%
- **Behavior**: Balanced spending across categories, occasional splurges

### 3. Affluent Executive
- **Income**: High
- **Spending Style**: Lavish
- **Preferred Categories**: Shopping, Travel, Food & Drink, Entertainment
- **Risk Tolerance**: 80%
- **Behavior**: High-value purchases, premium brands, frequent dining

---

## 📊 Realistic Merchant Patterns

### Temporal Dynamics

Each merchant has unique behavioral patterns:

| Merchant | Frequency | Peak Hours | Weekend Multiplier | Loyalty Discount |
|----------|-----------|------------|-------------------|------------------|
| **Starbucks** | Daily | 7-9am, 2-3pm | 0.7x | 10% off |
| **Uber** | Weekly | 7-8am, 5-6pm, 10-11pm | 1.4x | None |
| **Whole Foods** | Weekly | 5-7pm | 1.3x | None |
| **Netflix** | Monthly | Midnight (auto-charge) | 1.0x | None |
| **Olive Garden** | Monthly | 6-9pm | 1.5x | None |

### Spending Patterns

- **Coffee Shops**: High frequency (60-90 transactions/90 days), low amount ($3-$12)
- **Groceries**: Weekly patterns, higher on weekends, variable amounts
- **Restaurants**: Lower frequency, higher amounts, peak dinner hours
- **Subscriptions**: Fixed monthly charges at midnight
- **Gas Stations**: Weekly refills, morning/evening commute times
- **E-commerce**: Evening browsing patterns (8-10pm)

---

## 🕐 Temporal Intelligence

### Time-of-Day Patterns
- **Morning Rush** (7-9am): Coffee, gas, breakfast
- **Lunch** (12-2pm): Fast casual restaurants
- **Evening Commute** (5-7pm): Groceries, gas, ride-sharing
- **Dinner** (6-9pm): Sit-down restaurants
- **Late Night** (10pm-2am): E-commerce browsing, ride-sharing

### Day-of-Week Patterns
- **Weekdays**: Commute-related, work lunch, subscriptions
- **Weekends**: 1.3-1.8x multiplier for restaurants, groceries, entertainment
- **Friday/Saturday Nights**: Higher ride-sharing, restaurant spending

### Seasonal Patterns
- **Holidays**: 1.3x spending multiplier
- **Month-End**: Utility bills, rent, subscriptions
- **Special Dates**: Valentine's Day, July 4th, Thanksgiving, Christmas

---

## 🚨 Complex Anomaly Types

### 1. Account Takeover
**Pattern**: Burst of 3-5 high-value transactions within 1-2 hours

**Characteristics**:
- Late night timing (2-5am) - suspicious
- High-value electronics ($800-$2,500)
- Multiple merchants in short time
- No prior history with these merchants

**Example**:
```
2:15am - Best Buy: $1,450.00
2:47am - Apple Store: $2,100.00
3:22am - Amazon: $890.00
```

**Detection**: Velocity + volumetric + temporal anomaly

---

### 2. Card Testing
**Pattern**: 5-10 small transactions ($1-$5) in rapid succession

**Characteristics**:
- Very small amounts to avoid detection
- Multiple different merchants
- Rapid-fire timing (minutes apart)
- Often late night or early morning

**Example**:
```
1:05am - Amazon: $0.99
1:08am - Target: $1.50
1:12am - Walmart: $2.25
1:15am - Amazon: $3.99
1:18am - Target: $1.75
```

**Detection**: Velocity + pattern + amount deviation

---

### 3. Geographic Anomaly
**Pattern**: Two transactions in impossible locations within short time

**Characteristics**:
- Same hour, different cities (impossible travel)
- One local, one distant
- Normal amounts (harder to detect)

**Example**:
```
8:00am - Starbucks (San Francisco): $6.50
8:30am - Best Buy (New York): $450.00
```

**Detection**: Geospatial + temporal impossibility

---

### 4. Velocity Anomaly
**Pattern**: 15-25 transactions in a single day (normal: 2-5)

**Characteristics**:
- Unusually high transaction frequency
- Multiple different merchants
- Spread throughout the day
- May indicate compromised card or bot activity

**Example**: 20 transactions across various merchants in one day

**Detection**: Transaction count deviation

---

### 5. Volumetric Anomalies
**Pattern**: Single transaction way above merchant's normal range

**Characteristics**:
- 5-20x normal spending for that merchant
- May be legitimate (catering, bulk purchase) or fraud
- Requires context to determine legitimacy

**Examples**:
- Starbucks: $287.50 (normal: $4-$12) - Catering order
- Shell Gas: $250.00 (normal: $35-$65) - Possible skimming
- Amazon: $1,249.99 (normal: $15-$120) - Laptop purchase

**Detection**: Z-score > 3.0 standard deviations

---

### 6. Duplicate Transactions
**Pattern**: Same merchant + same amount within 24 hours

**Characteristics**:
- Exact amount match
- Same merchant
- Short time window
- May indicate double billing or processing error

**Example**:
```
6:15pm - Uber: $18.75
6:18pm - Uber: $18.75
```

**Detection**: Exact match within time window

---

## 📈 Statistical Properties

### Normal Distribution
- Transaction amounts follow **normal distribution** within merchant ranges
- Mean: (min + max) / 2
- Std Dev: (max - min) / 6 (99.7% within range)

### Variance Factors
- ±10% random variance on all amounts
- Weekend multipliers (0.6x to 1.8x)
- Holiday multipliers (1.3x)
- Loyalty discounts (5-15% off)
- Time-of-day multipliers (0.3x to 1.2x)

### Frequency Distribution
- **Daily**: 60-90 transactions/90 days
- **Weekly**: 10-15 transactions/90 days
- **Biweekly**: 5-8 transactions/90 days
- **Monthly**: 2-4 transactions/90 days
- **Quarterly**: 1-2 transactions/90 days

---

## 🎯 Dataset Statistics

### Generated Data (90 days)
- **Total Transactions**: ~240-250
- **Normal Transactions**: ~200-210
- **Anomalous Transactions**: ~40
- **Unique Merchants**: 30
- **Categories**: 8 (Food & Drink, Groceries, Transportation, Shopping, Electronics, Entertainment, Utilities, Health)

### Anomaly Breakdown
- Account Takeover: 3-5 transactions
- Card Testing: 5-10 transactions
- Geographic: 2 transactions
- Velocity: 15-25 transactions
- Volumetric: 5 transactions
- Duplicate: 2 transactions

---

## 🔬 Why This Is Advanced

### 1. **Temporal Realism**
- Not just random dates - considers time-of-day, day-of-week, holidays
- Peak hours vary by merchant type
- Weekend patterns differ from weekdays

### 2. **Behavioral Modeling**
- User personas with consistent spending habits
- Loyalty patterns (repeat customers get discounts)
- Category preferences based on income/lifestyle

### 3. **Statistical Rigor**
- Normal distributions with proper variance
- Multiple multipliers compound realistically
- Amounts clamped to realistic ranges

### 4. **Complex Anomalies**
- Not just "big numbers" - sophisticated fraud patterns
- Account takeover mimics real attack vectors
- Card testing follows actual criminal behavior
- Geographic anomalies test spatial reasoning

### 5. **Production-Grade Patterns**
- Subscriptions charge at midnight
- Gas stations cluster around commute times
- Restaurants peak at meal times
- E-commerce peaks in evening

---

## 🚀 Usage

### Generate New Dataset

```bash
cd backend
python clear_and_inject.py
```

### Customize Parameters

Edit `advanced_data_generator.py`:

```python
# Change time window
generate_advanced_dataset(days=180)  # 6 months instead of 90 days

# Modify personas
PERSONAS.append(UserPersona(
    name="Retired Senior",
    income_bracket="medium",
    spending_style="frugal",
    preferred_categories=["Groceries", "Health", "Utilities"],
    risk_tolerance=0.1,
))

# Add new merchants
MERCHANT_DATABASE["Your Merchant"] = {
    "category": "Your Category",
    "base_range": (10.00, 50.00),
    "frequency": "weekly",
    "peak_hours": [12, 13, 14],
    "weekend_multiplier": 1.2,
    "loyalty_discount": 0.95,
}
```

---

## 📚 Interview Talking Points

### "Why is your data generation sophisticated?"

> "I implemented user personas with distinct spending behaviors, temporal patterns including time-of-day and seasonal effects, and six complex anomaly types that mirror real-world fraud patterns like account takeover and card testing. Each merchant has unique behavioral characteristics - for example, Starbucks peaks at 7-9am with a 0.7x weekend multiplier, while Olive Garden peaks at 6-9pm with a 1.5x weekend multiplier. This goes beyond random data generation to model actual consumer behavior."

### "How do you ensure statistical validity?"

> "Transaction amounts follow normal distributions with mean at the midpoint of the merchant's range and standard deviation calculated to keep 99.7% of values within bounds. I apply multiple variance factors - weekend multipliers, holiday effects, loyalty discounts, and time-of-day adjustments - that compound realistically. The frequency distributions are also statistically grounded, with daily merchants generating 60-90 transactions over 90 days while quarterly merchants generate 1-2."

### "What makes your anomalies realistic?"

> "I modeled six distinct fraud patterns based on actual attack vectors: account takeover (burst of high-value purchases at 2-5am), card testing (5-10 micro-transactions to validate stolen cards), geographic anomalies (impossible travel times), velocity anomalies (20+ transactions in one day), volumetric anomalies (5-20x normal spending), and duplicate transactions. These aren't just 'big numbers' - they're sophisticated patterns that require multi-dimensional detection."

---

## 🎓 Learning Resources

- **Fraud Detection Patterns**: [Stripe Radar](https://stripe.com/docs/radar/rules)
- **Temporal Modeling**: [Time Series Analysis](https://otexts.com/fpp3/)
- **Behavioral Economics**: [Predictably Irrational](https://www.amazon.com/Predictably-Irrational-Hidden-Forces-Decisions/dp/0061353248)
- **Statistical Distributions**: [Normal Distribution](https://en.wikipedia.org/wiki/Normal_distribution)

---

**This advanced data generation demonstrates production-level thinking and sets your project apart from basic tutorials.** 🚀
