"""
Network Graph API for fraud ring visualization.

Provides graph data (nodes, edges, rings) for interactive network visualization.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import Account, AccountLink, SessionLocal, Transaction, User
from detection.fraud_ring import detect_fraud_ring

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/graph", tags=["graph"])

# Simple in-memory cache (30 seconds TTL)
_cache: dict[str, Any] = {}
_cache_timestamp: datetime | None = None
CACHE_TTL_SECONDS = 30


def get_db() -> Session:
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/network")
async def get_network_graph(
    window_hours: int = Query(24, ge=1, le=168, description="Time window for edges"),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    Get network graph data for visualization.
    
    Returns nodes (accounts), edges (transaction flows), and fraud rings
    with risk scoring and velocity metrics.
    
    Args:
        window_hours: Time window for transaction analysis (1-168 hours)
        db: Database session
    
    Returns:
        Graph data with nodes, edges, rings, and metadata
    """
    global _cache, _cache_timestamp
    
    # Check cache
    cache_key = f"network_{window_hours}"
    if (
        _cache_timestamp
        and (datetime.utcnow() - _cache_timestamp).total_seconds() < CACHE_TTL_SECONDS
        and cache_key in _cache
    ):
        logger.info("Returning cached graph data")
        return _cache[cache_key]
    
    logger.info(f"Building network graph (window={window_hours}h)")
    
    # Step 1: Build nodes (accounts)
    nodes = await build_nodes(db)
    
    # Step 2: Build edges (transaction flows between accounts)
    edges = await build_edges(db, window_hours)
    
    # Step 3: Detect fraud rings
    rings = detect_fraud_ring(db, window_hours)
    
    # Step 4: Update node risk scores based on edges and rings
    nodes = update_node_risk_scores(nodes, edges, rings)
    
    # Step 5: Build metadata
    metadata = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "active_rings": len(rings),
        "max_risk_score": max((n["risk_score"] for n in nodes), default=0.0),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "window_hours": window_hours
    }
    
    result = {
        "nodes": nodes,
        "edges": edges,
        "rings": rings,
        "metadata": metadata
    }
    
    # Update cache
    _cache[cache_key] = result
    _cache_timestamp = datetime.utcnow()
    
    logger.info(f"Graph built: {len(nodes)} nodes, {len(edges)} edges, {len(rings)} rings")
    
    return result


async def build_nodes(db: Session) -> list[dict[str, Any]]:
    """
    Build node list from accounts.
    
    Args:
        db: Database session
    
    Returns:
        List of node objects with account metadata
    """
    accounts = db.query(Account).all()
    nodes = []
    
    for account in accounts:
        # Get user
        user = db.query(User).get(account.user_id)
        
        # Count transactions
        txn_count = db.query(Transaction).filter(
            Transaction.account_id == account.id
        ).count()
        
        # Calculate total volume
        total_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account.id
        ).scalar() or 0.0
        
        # Determine persona from user name
        persona = "unknown"
        if user:
            if "Sarah" in user.name:
                persona = "sarah"
            elif "Mike" in user.name:
                persona = "mike"
            elif "TechStart" in user.name or "LLC" in user.name:
                persona = "techstart"
        
        # Initial risk score (will be updated later)
        risk_score = 0.15 if user and user.risk_profile == "low" else 0.5
        
        nodes.append({
            "id": account.account_id,
            "label": f"{user.name if user else 'Unknown'} - {account.account_type.title()}",
            "persona": persona,
            "account_type": account.account_type,
            "risk_score": risk_score,
            "transaction_count": txn_count,
            "total_volume": round(total_volume, 2),
            "status": "normal",
            "flagged": False,
            "balance": round(account.balance, 2)
        })
    
    return nodes


async def build_edges(db: Session, window_hours: int) -> list[dict[str, Any]]:
    """
    Build edge list from cross-account transactions and account links.
    
    Args:
        db: Database session
        window_hours: Time window for transaction analysis
    
    Returns:
        List of edge objects with transaction flow metrics
    """
    edges = []
    edge_id_counter = 1
    
    # Get account links
    links = db.query(AccountLink).all()
    
    # Get recent transactions
    cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
    recent_txns = db.query(Transaction).filter(
        Transaction.created_at >= cutoff_time,
        Transaction.account_id.isnot(None)
    ).all()
    
    # Build edges from account links
    for link in links:
        # Get accounts
        account_a = db.query(Account).get(link.account_a_id)
        account_b = db.query(Account).get(link.account_b_id)
        
        if not account_a or not account_b:
            continue
        
        # Count transactions between these accounts in window
        # (For now, we'll use link strength as proxy since we don't have direct transfers)
        # In a real system, you'd query for transfers between accounts
        
        # Get transactions from both accounts to same merchants (proxy for interaction)
        txns_a = [t for t in recent_txns if t.account_id == account_a.id]
        txns_b = [t for t in recent_txns if t.account_id == account_b.id]
        
        # Find common merchants
        merchants_a = set(t.merchant_name for t in txns_a if t.merchant_name)
        merchants_b = set(t.merchant_name for t in txns_b if t.merchant_name)
        common_merchants = merchants_a & merchants_b
        
        if not common_merchants:
            # Still create edge based on link, but with minimal activity
            transaction_count = 0
            total_amount = 0.0
            time_clustered_txns = 0
            velocity_score = link.strength * 0.3
        else:
            # Calculate metrics based on common merchant activity
            common_txns_a = [t for t in txns_a if t.merchant_name in common_merchants]
            common_txns_b = [t for t in txns_b if t.merchant_name in common_merchants]
            
            transaction_count = len(common_txns_a) + len(common_txns_b)
            total_amount = sum(t.amount for t in common_txns_a + common_txns_b)
            
            # Detect time clustering (transactions within 5 minutes)
            time_clustered_txns = count_time_clustered_transactions(
                common_txns_a + common_txns_b
            )
            
            # Calculate velocity score
            velocity_score = calculate_velocity_score(
                transaction_count,
                time_clustered_txns,
                window_hours
            )
        
        # Calculate risk score
        risk_score = calculate_edge_risk_score(
            link.link_type,
            link.strength,
            velocity_score,
            time_clustered_txns
        )
        
        # Determine anomaly flags
        anomaly_flags = []
        if velocity_score > 0.7:
            anomaly_flags.append("velocity_burst")
        if time_clustered_txns > 2:
            anomaly_flags.append("time_clustering")
        if link.link_type in ["shared_device", "shared_ip"]:
            anomaly_flags.append("suspicious_link")
        
        # Get last transaction time
        all_txns = common_txns_a + common_txns_b if common_merchants else []
        last_transaction = max(
            (t.created_at for t in all_txns),
            default=link.detected_at
        ).isoformat() + "Z"
        
        edges.append({
            "id": f"edge_{edge_id_counter:03d}",
            "source": account_a.account_id,
            "target": account_b.account_id,
            "transaction_count": transaction_count,
            "total_amount": round(total_amount, 2),
            "velocity_score": round(velocity_score, 2),
            "time_clustered_txns": time_clustered_txns,
            "risk_score": round(risk_score, 2),
            "last_transaction": last_transaction,
            "anomaly_flags": anomaly_flags,
            "link_type": link.link_type,
            "link_strength": round(link.strength, 2)
        })
        
        edge_id_counter += 1
    
    return edges


def count_time_clustered_transactions(transactions: list[Transaction]) -> int:
    """
    Count transactions that occur within 5 minutes of each other.
    
    Args:
        transactions: List of transactions
    
    Returns:
        Count of time-clustered transactions
    """
    if len(transactions) < 2:
        return 0
    
    # Sort by created_at
    sorted_txns = sorted(transactions, key=lambda t: t.created_at)
    
    clustered_count = 0
    for i in range(len(sorted_txns) - 1):
        time_diff = (sorted_txns[i + 1].created_at - sorted_txns[i].created_at).total_seconds() / 60
        if time_diff <= 5:
            clustered_count += 1
    
    return clustered_count


def calculate_velocity_score(
    transaction_count: int,
    time_clustered_txns: int,
    window_hours: int
) -> float:
    """
    Calculate velocity score (0.0-1.0) based on transaction frequency.
    
    Args:
        transaction_count: Total transactions in window
        time_clustered_txns: Transactions within 5-minute clusters
        window_hours: Time window size
    
    Returns:
        Velocity score (0.0-1.0)
    """
    if transaction_count == 0:
        return 0.0
    
    # Normalize transaction count (assume 10 txns per day is high)
    expected_txns = (window_hours / 24) * 10
    txn_ratio = min(transaction_count / expected_txns, 1.0)
    
    # Clustering ratio
    cluster_ratio = time_clustered_txns / transaction_count if transaction_count > 0 else 0.0
    
    # Weighted score
    velocity_score = 0.6 * txn_ratio + 0.4 * cluster_ratio
    
    return min(velocity_score, 1.0)


def calculate_edge_risk_score(
    link_type: str,
    link_strength: float,
    velocity_score: float,
    time_clustered_txns: int
) -> float:
    """
    Calculate edge risk score (0.0-1.0).
    
    Args:
        link_type: Type of account link
        link_strength: Link confidence (0.0-1.0)
        velocity_score: Transaction velocity score
        time_clustered_txns: Count of time-clustered transactions
    
    Returns:
        Risk score (0.0-1.0)
    """
    # Base risk from link type
    base_risk = {
        "family": 0.1,
        "business": 0.2,
        "shared_device": 0.6,
        "shared_ip": 0.7
    }.get(link_type, 0.5)
    
    # Adjust by velocity
    risk = base_risk + (velocity_score * 0.3)
    
    # Penalty for time clustering
    if time_clustered_txns > 2:
        risk += 0.2
    
    # Adjust by link strength (suspicious links with high strength are riskier)
    if link_type in ["shared_device", "shared_ip"]:
        risk += link_strength * 0.1
    
    return min(risk, 1.0)


def update_node_risk_scores(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    rings: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Update node risk scores based on connected edges and fraud ring membership.
    
    Args:
        nodes: List of node objects
        edges: List of edge objects
        rings: List of fraud ring objects
    
    Returns:
        Updated node list with risk scores
    """
    # Build node ID to node mapping
    node_map = {node["id"]: node for node in nodes}
    
    # Build edge risk map
    edge_risks = {}
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        risk = edge["risk_score"]
        
        if source not in edge_risks:
            edge_risks[source] = []
        if target not in edge_risks:
            edge_risks[target] = []
        
        edge_risks[source].append(risk)
        edge_risks[target].append(risk)
    
    # Build ring membership map
    ring_members = set()
    for ring in rings:
        for account_id in ring.get("accounts_involved", []):
            ring_members.add(account_id)
    
    # Update node risk scores
    for node in nodes:
        node_id = node["id"]
        
        # Max edge risk
        if node_id in edge_risks:
            max_edge_risk = max(edge_risks[node_id])
            node["risk_score"] = max_edge_risk
        
        # Ring membership bonus
        if node_id in ring_members:
            node["risk_score"] = min(1.0, node["risk_score"] + 0.15)
            node["flagged"] = True
            node["status"] = "fraud_ring"
        elif node["risk_score"] > 0.6:
            node["flagged"] = True
            node["status"] = "high_risk"
        elif node["risk_score"] > 0.3:
            node["status"] = "elevated"
        else:
            node["status"] = "normal"
        
        # Round risk score
        node["risk_score"] = round(node["risk_score"], 2)
    
    return nodes
