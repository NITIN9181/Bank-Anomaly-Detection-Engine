import math
from typing import Dict, List, Any

def calculate_feature_contributions(transaction: Dict[str, Any], vendor_profile: Dict[str, Any], z_score: float, isolation_score: float) -> List[Dict[str, Any]]:
    """
    Calculate normalized feature contributions for explainability.
    Ensures contributions sum to ~1.0.
    """
    contributions = []
    
    # 1. Volumetric / Z-Score Layer
    amount = transaction.get("amount", 0)
    baseline_amount = vendor_profile.get("avg_amount", 0) if vendor_profile else 0
    norm_z = min(1.0, abs(z_score) / 5.0)  # cap at 5 sigma
    z_contrib = norm_z * 0.4
    
    if z_contrib > 0.05:
        contributions.append({
            "feature_name": "amount_deviation",
            "display_name": "Amount Deviation",
            "value": amount,
            "baseline": baseline_amount,
            "contribution_score": z_contrib,
            "direction": "positive" if amount > baseline_amount else "negative",
            "description": f"Transaction amount is significantly different from vendor average",
            "category": "volumetric"
        })

    # 2. ML / Isolation Forest Layer
    # Assuming lower isolation score means more anomalous (e.g., negative scores in sklearn)
    # Threshold usually around -0.15 to 0
    norm_iso = min(1.0, max(0.0, abs(isolation_score) / 0.5))
    iso_contrib = norm_iso * 0.35
    
    if iso_contrib > 0.05:
        contributions.append({
            "feature_name": "ml_anomaly",
            "display_name": "Complex Pattern Deviation",
            "value": isolation_score,
            "baseline": -0.1,  # typical baseline
            "contribution_score": iso_contrib,
            "direction": "positive",
            "description": "Multi-dimensional feature vector flagged by Isolation Forest model",
            "category": "structural"
        })

    # 3. Behavioral / Velocity Layer
    # Simple proxy if not explicitly passed: Check time diffs if available
    velocity = transaction.get("velocity_score", 0) 
    velocity_contrib = min(1.0, velocity) * 0.15
    if velocity_contrib > 0.05:
         contributions.append({
            "feature_name": "velocity_cluster",
            "display_name": "Velocity Cluster",
            "value": velocity,
            "baseline": 1.2,
            "contribution_score": velocity_contrib,
            "direction": "positive",
            "description": "High frequency of transactions in a short time window",
            "category": "behavioral"
        })

    # 4. Temporal / Structural Layer (Merchant Rarity)
    rarity = transaction.get("merchant_rarity", 0)
    rarity_contrib = min(1.0, rarity / 0.5) * 0.10
    if rarity_contrib > 0.02:
        contributions.append({
            "feature_name": "merchant_rarity",
            "display_name": "Merchant Rarity",
            "value": rarity,
            "baseline": 0.15,
            "contribution_score": rarity_contrib,
            "direction": "positive",
            "description": "This merchant rarely appears in historical transaction data",
            "category": "structural"
        })

    # Normalize contributions to sum to 1.0
    total = sum(c["contribution_score"] for c in contributions)
    if total > 0:
        for c in contributions:
            c["contribution_score"] = round(c["contribution_score"] / total, 2)

    return sorted(contributions, key=lambda x: x["contribution_score"], reverse=True)
