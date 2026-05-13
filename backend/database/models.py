"""
SQLAlchemy ORM models for Bank Anomaly Detection Engine.

Defines three core entities:
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
from sqlalchemy.orm import sessionmaker

from config import settings

Base = declarative_base()


class Transaction(Base):
    """
    Banking transaction record from Plaid API.
    
    Attributes:
        id: Primary key
        plaid_transaction_id: Unique Plaid transaction identifier (deduplication key)
        account_id: Plaid account identifier
        amount: Transaction amount (positive=debit, negative=credit)
        date: Transaction date in YYYY-MM-DD format
        merchant_name: Normalized merchant name
        category: Transaction category from Plaid
        created_at: Record creation timestamp
    """
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plaid_transaction_id = Column(String, unique=True, nullable=False, index=True)
    account_id = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD format
    merchant_name = Column(String, nullable=True, index=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


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
