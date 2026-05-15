"""
Cross-Account Fraud Ring Detection.

Detects coordinated spending patterns across multiple accounts that may
indicate fraud rings, money laundering, or account takeover attacks.
"""

from __future__ import annotations

import hashlib
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from database.models import Account, AccountLink, Transaction

# Configure logging
logger = logging.getLogger(__name__)


def detect_fraud_ring(db: Session, window_hours: int = 24) -> list[dict[str, Any]]:
    """
    Detect potential fraud rings via cross-account velocity analysis.
    
    Detection logic:
    1. Query transactions in last window_hours
    2. Group by merchant_name
    3. For each merchant, find accounts with transactions within 5-minute clusters
    4. If >= 3 accounts hit same merchant within 5 minutes:
       - Check AccountLink: are these accounts linked?
       - If linked + high velocity: "coordinated_spending" (low risk)
       - If NOT linked + high velocity: "fraud_ring" (high risk)
    
    Args:
        db: Database session
        window_hours: Time window to analyze (default 24 hours)
    
    Returns:
        List of fraud ring objects with risk scores
    """
    logger.info(f"Starting fraud ring detection (window={window_hours}h)")
    
    # Step 1: Get recent transactions
    cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
    
    recent_txns = db.query(Transaction).filter(
        Transaction.created_at >= cutoff_time,
        Transaction.account_id.isnot(None),  # Must have account
        Transaction.merchant_name.isnot(None)  # Must have merchant
    ).all()
    
    logger.info(f"Found {len(recent_txns)} transactions in window")
    
    if len(recent_txns) < 3:
        logger.info("Not enough transactions for ring detection")
        return []
    
    # Step 2: Group by merchant
    merchant_groups = defaultdict(list)
    for txn in recent_txns:
        merchant_groups[txn.merchant_name].append(txn)
    
    # Step 3: Detect clusters within each merchant
    fraud_rings = []
    
    for merchant, txns in merchant_groups.items():
        if len(txns) < 3:
            continue  # Need at least 3 transactions
        
        # Sort by created_at
        txns_sorted = sorted(txns, key=lambda t: t.created_at)
        
        # Find 5-minute clusters
        clusters = find_time_clusters(txns_sorted, max_minutes=5)
        
        for cluster in clusters:
            if len(cluster) < 3:
                continue  # Need at least 3 accounts
            
            # Get unique accounts in cluster
            account_ids = list(set(txn.account_id for txn in cluster))
            
            if len(account_ids) < 3:
                continue  # Need at least 3 different accounts
            
            # Check if accounts are linked
            link_info = check_account_links(db, account_ids)
            
            # Calculate metrics
            total_amount = sum(txn.amount for txn in cluster)
            time_window_minutes = (
                (cluster[-1].created_at - cluster[0].created_at).total_seconds() / 60
            )
            
            # Determine anomaly type and risk
            if link_info["has_links"] and link_info["link_type"] in ["family", "business"]:
                anomaly_type = "coordinated_spending"
                base_risk = 0.3  # Lower risk for legitimate links
            else:
                anomaly_type = "fraud_ring"
                base_risk = 0.7  # Higher risk for unlinked accounts
            
            # Calculate risk score
            risk_score = calculate_ring_risk_score(
                base_risk=base_risk,
                has_links=link_info["has_links"],
                time_window_minutes=time_window_minutes,
                total_amount=total_amount,
                account_count=len(account_ids)
            )
            
            # Generate ring ID
            ring_id = generate_ring_id(merchant, account_ids, cluster[0].created_at)
            
            fraud_rings.append({
                "ring_id": ring_id,
                "accounts_involved": [f"acc_{aid}" for aid in account_ids],
                "merchant": merchant,
                "transaction_count": len(cluster),
                "total_amount": round(total_amount, 2),
                "time_window_minutes": round(time_window_minutes, 2),
                "link_type": link_info["link_type"] if link_info["has_links"] else "none",
                "risk_score": round(risk_score, 2),
                "anomaly_type": anomaly_type,
                "detected_at": datetime.utcnow().isoformat() + "Z"
            })
    
    logger.info(f"Detected {len(fraud_rings)} potential fraud rings")
    return fraud_rings


def find_time_clusters(
    transactions: list[Transaction],
    max_minutes: int = 5
) -> list[list[Transaction]]:
    """
    Find clusters of transactions within max_minutes of each other.
    
    Args:
        transactions: Sorted list of transactions
        max_minutes: Maximum time gap between transactions in a cluster
    
    Returns:
        List of transaction clusters
    """
    if not transactions:
        return []
    
    clusters = []
    current_cluster = [transactions[0]]
    
    for txn in transactions[1:]:
        time_diff = (txn.created_at - current_cluster[-1].created_at).total_seconds() / 60
        
        if time_diff <= max_minutes:
            current_cluster.append(txn)
        else:
            if len(current_cluster) >= 3:
                clusters.append(current_cluster)
            current_cluster = [txn]
    
    # Don't forget the last cluster
    if len(current_cluster) >= 3:
        clusters.append(current_cluster)
    
    return clusters


def check_account_links(db: Session, account_ids: list[int]) -> dict[str, Any]:
    """
    Check if accounts have any links between them.
    
    Args:
        db: Database session
        account_ids: List of account IDs to check
    
    Returns:
        Dictionary with link information
    """
    # Query for any links between these accounts
    links = db.query(AccountLink).filter(
        AccountLink.account_a_id.in_(account_ids),
        AccountLink.account_b_id.in_(account_ids)
    ).all()
    
    if not links:
        return {
            "has_links": False,
            "link_type": None,
            "max_strength": 0.0
        }
    
    # Find strongest link
    max_strength = max(link.strength for link in links)
    primary_link_type = max(links, key=lambda l: l.strength).link_type
    
    return {
        "has_links": True,
        "link_type": primary_link_type,
        "max_strength": max_strength
    }


def calculate_ring_risk_score(
    base_risk: float,
    has_links: bool,
    time_window_minutes: float,
    total_amount: float,
    account_count: int
) -> float:
    """
    Calculate fraud ring risk score (0.0 to 1.0).
    
    Scoring factors:
    - Base: 0.5 (or provided base_risk)
    - +0.3 if accounts NOT linked
    - +0.1 if time_window < 2 minutes
    - +0.1 if total_amount > $50,000
    - +0.05 per account beyond 3
    
    Args:
        base_risk: Base risk score
        has_links: Whether accounts have legitimate links
        time_window_minutes: Time span of cluster
        total_amount: Total transaction amount
        account_count: Number of accounts involved
    
    Returns:
        Risk score capped at 1.0
    """
    score = base_risk
    
    # Penalty for unlinked accounts
    if not has_links:
        score += 0.3
    
    # Penalty for very tight timing
    if time_window_minutes < 2.0:
        score += 0.1
    
    # Penalty for high amounts
    if total_amount > 50000.0:
        score += 0.1
    
    # Penalty for many accounts
    if account_count > 3:
        score += 0.05 * (account_count - 3)
    
    # Cap at 1.0
    return min(score, 1.0)


def generate_ring_id(merchant: str, account_ids: list[int], timestamp: datetime) -> str:
    """
    Generate unique ring ID from merchant, accounts, and timestamp.
    
    Args:
        merchant: Merchant name
        account_ids: List of account IDs
        timestamp: Detection timestamp
    
    Returns:
        Unique ring ID (e.g., "ring_abc123")
    """
    # Sort account IDs for consistency
    sorted_ids = sorted(account_ids)
    
    # Create hash input
    hash_input = f"{merchant}_{sorted_ids}_{timestamp.isoformat()}"
    
    # Generate short hash
    hash_obj = hashlib.md5(hash_input.encode())
    short_hash = hash_obj.hexdigest()[:6]
    
    return f"ring_{short_hash}"
