from typing import List, Dict, Any

def get_recommended_actions(features: List[Dict[str, Any]], overall_confidence: float, is_duplicate: bool) -> List[Dict[str, Any]]:
    """
    Rule-based recommendation engine for anomaly resolution.
    Returns actions sorted by priority (1 is highest).
    """
    actions = []
    
    # Create lookup map
    feat_map = {f["feature_name"]: f["value"] for f in features}
    contrib_map = {f["feature_name"]: f["contribution_score"] for f in features}

    if is_duplicate:
        actions.append({
            "action_id": "check_duplicate",
            "priority": 1,
            "label": "Check for Duplicate Charge",
            "description": "System flagged this as an exact duplicate of a recent transaction.",
            "automation_possible": True,
            "estimated_time": "1 min",
            "icon": "copy"
        })

    amount_dev = contrib_map.get("amount_deviation", 0)
    if amount_dev > 0.4:
        actions.append({
            "action_id": "review_vendor",
            "priority": 1 if not is_duplicate else 2,
            "label": "Review with Vendor",
            "description": "Contact the merchant to verify this significant charge deviation.",
            "automation_possible": False,
            "estimated_time": "5 min",
            "icon": "phone"
        })

    vel_cluster = contrib_map.get("velocity_cluster", 0)
    if vel_cluster > 0.3:
        actions.append({
            "action_id": "verify_cardholder",
            "priority": 2,
            "label": "Verify with Cardholder",
            "description": "Confirm high-velocity clustering with the account owner.",
            "automation_possible": True,
            "estimated_time": "2 min",
            "icon": "shield"
        })

    rarity = feat_map.get("merchant_rarity", 0)
    if rarity > 0.2:
        actions.append({
            "action_id": "verify_merchant",
            "priority": 2,
            "label": "Verify Merchant Legitimacy",
            "description": "Investigate this unusual merchant profile.",
            "automation_possible": False,
            "estimated_time": "10 min",
            "icon": "search"
        })

    if overall_confidence < 0.5:
        actions.append({
            "action_id": "manual_review",
            "priority": 3,
            "label": "Manual Review Required",
            "description": "Model confidence is low. Requires human judgment.",
            "automation_possible": False,
            "estimated_time": "15 min",
            "icon": "user"
        })
        
    # Default fallback action
    actions.append({
        "action_id": "mark_false_positive",
        "priority": 3 if overall_confidence >= 0.5 else 4,
        "label": "Mark False Positive",
        "description": "Anomaly appears legitimate upon review.",
        "automation_possible": True,
        "estimated_time": "1 min",
        "icon": "check"
    })

    return sorted(actions, key=lambda x: x["priority"])
