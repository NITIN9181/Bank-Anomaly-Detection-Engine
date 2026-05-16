"""
SQLAlchemy ORM models for Bank Anomaly Detection Engine.

Defines core entities:
- User: Account holder with risk profile
- Account: Bank account (checking, savings, business)
- AccountLink: Relationships between accounts (family, business, fraud rings)
- Transaction: Raw banking transactions from Plaid
- VendorProfile: Aggregated statistics per merchant
- Anomaly: Detected anomalies with explanations
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from config import settings

Base = declarative_base()


class User(Base):
    """
    Account holder with spending profile and risk assessment.
    
    Attributes:
        id: Primary key
        user_id: Unique user identifier (e.g., "user_456")
        name: User's full name
        risk_profile: Risk classification (low, medium, high)
        typical_monthly_spend: Expected monthly spending baseline
        payroll_day: Day of month salary typically arrives (1-31)
        created_at: Record creation timestamp
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    risk_profile = Column(
        String,
        CheckConstraint(
            "risk_profile IN ('low', 'medium', 'high')",
            name="check_risk_profile"
        ),
        default="medium",
        nullable=False
    )
    typical_monthly_spend = Column(Float, nullable=True)
    payroll_day = Column(Integer, nullable=True)  # 1-31
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    accounts = relationship("Account", back_populates="user")


class Account(Base):
    """
    Bank account with balance and type classification.
    
    Attributes:
        id: Primary key
        account_id: Unique account identifier (e.g., "acc_123")
        user_id: Foreign key to users table
        account_type: Account classification (checking, savings, business)
        balance: Current account balance
        created_at: Record creation timestamp
    """
    
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    account_type = Column(
        String,
        CheckConstraint(
            "account_type IN ('checking', 'savings', 'business')",
            name="check_account_type"
        ),
        nullable=False
    )
    balance = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    
    # Account links (many-to-many via AccountLink)
    links_as_a = relationship(
        "AccountLink",
        foreign_keys="AccountLink.account_a_id",
        back_populates="account_a"
    )
    links_as_b = relationship(
        "AccountLink",
        foreign_keys="AccountLink.account_b_id",
        back_populates="account_b"
    )


class AccountLink(Base):
    """
    Relationship between two accounts for fraud ring detection.
    
    Links can represent legitimate relationships (family, business) or
    suspicious patterns (shared device, shared IP).
    
    Attributes:
        id: Primary key
        account_a_id: First account in relationship
        account_b_id: Second account in relationship
        link_type: Relationship classification
        strength: Confidence score (0.0-1.0)
        detected_at: Link detection timestamp
    """
    
    __tablename__ = "account_links"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_a_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    account_b_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    link_type = Column(
        String,
        CheckConstraint(
            "link_type IN ('shared_device', 'shared_ip', 'family', 'business')",
            name="check_link_type"
        ),
        nullable=False
    )
    strength = Column(Float, nullable=False)  # 0.0 to 1.0
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account_a = relationship(
        "Account",
        foreign_keys=[account_a_id],
        back_populates="links_as_a"
    )
    account_b = relationship(
        "Account",
        foreign_keys=[account_b_id],
        back_populates="links_as_b"
    )


class Transaction(Base):
    """
    Banking transaction record from Plaid API.
    
    Attributes:
        id: Primary key
        plaid_transaction_id: Unique Plaid transaction identifier (deduplication key)
        account_id: Foreign key to accounts table (nullable for backward compat)
        amount: Transaction amount (positive=debit, negative=credit)
        date: Transaction date in YYYY-MM-DD format
        merchant_name: Normalized merchant name
        category: Transaction category from Plaid
        created_at: Record creation timestamp
    """
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plaid_transaction_id = Column(String, unique=True, nullable=False, index=True)
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,  # Nullable for backward compatibility
        index=True
    )
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD format
    merchant_name = Column(String, nullable=True, index=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")


class VendorProfile(Base):
    """
    Aggregated statistics per merchant for anomaly detection.
    
    Computed from rolling 6-month transaction history.
    
    Attributes:
        id: Primary key
        merchant_name: Unique merchant identifier
        category: Primary transaction category
        avg_amount: 6-month rolling mean
        std_amount: 6-month rolling standard deviation
        transaction_count: Total transactions in window
        last_updated: Last profile computation timestamp
    """
    
    __tablename__ = "vendor_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=True)
    avg_amount = Column(Float, nullable=True)
    std_amount = Column(Float, nullable=True)
    transaction_count = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, nullable=True)


class Anomaly(Base):
    """
    Detected transaction anomaly with ML scores and LLM explanation.
    
    Attributes:
        id: Primary key
        transaction_id: Foreign key to transactions table
        anomaly_type: Classification (volumetric, deviant_pattern, duplicate)
        z_score: Statistical deviation score (null for non-statistical anomalies)
        isolation_score: Isolation Forest score (lower = more anomalous)
        explanation: Natural language explanation from LLM
        detected_at: Detection timestamp
        status: Review status (flagged, resolved, false_positive)
    """
    
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    anomaly_type = Column(
        String,
        CheckConstraint(
            "anomaly_type IN ('volumetric', 'deviant_pattern', 'duplicate')",
            name="check_anomaly_type"
        ),
        nullable=False
    )
    z_score = Column(Float, nullable=True)
    isolation_score = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(
        String,
        CheckConstraint(
            "status IN ('flagged', 'resolved', 'false_positive')",
            name="check_status"
        ),
        default="flagged",
        nullable=False,
        index=True
    )
    explanation_confidence = Column(Float, default=0.0)
    feature_contributions = Column(Text, nullable=True) # store as JSON string
    recommended_actions = Column(Text, nullable=True) # store as JSON string
    analyst_feedback = Column(Text, nullable=True)
    feedback_score = Column(Integer, default=0)
    action_taken = Column(String, nullable=True)
    explanation_generated_at = Column(DateTime, nullable=True)
    
    # Relationship to Transaction
    transaction = relationship("Transaction", backref="anomalies")


# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints on SQLite connection."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Database engine and session factory
engine = create_engine(
    f"sqlite:///{settings.DATABASE_PATH}",
    connect_args={"check_same_thread": False},  # Allow multi-threaded access
    echo=False  # Set to True for SQL query logging during development
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def create_tables() -> None:
    """Create all database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
