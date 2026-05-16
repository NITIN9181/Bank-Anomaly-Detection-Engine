from typing import Dict, Any
from .confidence import compute_confidence
from .engine import calculate_feature_contributions

def simulate_what_if(original_data: Dict[str, Any], vendor_profile: Dict[str, Any], sim_params: Dict[str, float]) -> Dict[str, Any]:
    """
    Accepts hypothetical feature values, re-runs detection math, 
    and returns whether anomaly would still flag + new confidence.
    """
    # Clone original data
    sim_data = original_data.copy()
    
    # Apply simulated params
    if "amount" in sim_params:
        sim_data["amount"] = sim_params["amount"]
        # Very rough approximation of new z-score based on amount change
        old_amount = original_data.get("amount", 1)
        old_z = original_data.get("z_score", 0)
        # Assuming linear relationship to mean for simulation purposes
        if old_amount > 0:
            sim_data["z_score"] = old_z * (sim_params["amount"] / old_amount)

    if "velocity" in sim_params:
        sim_data["velocity_score"] = sim_params["velocity"]
        
    # Re-calculate confidence
    orig_conf = compute_confidence(original_data)
    sim_conf = compute_confidence(sim_data)
    
    # Re-calculate features
    orig_feats = calculate_feature_contributions(original_data, vendor_profile, original_data.get("z_score", 0), original_data.get("isolation_score", 0))
    sim_feats = calculate_feature_contributions(sim_data, vendor_profile, sim_data.get("z_score", 0), original_data.get("isolation_score", 0))
    
    changed_features = []
    
    orig_feat_map = {f["feature_name"]: f for f in orig_feats}
    sim_feat_map = {f["feature_name"]: f for f in sim_feats}
    
    for fname, orig_f in orig_feat_map.items():
        sim_f = sim_feat_map.get(fname)
        if sim_f and abs(sim_f["contribution_score"] - orig_f["contribution_score"]) > 0.01:
            impact_diff = (orig_f["contribution_score"] - sim_f["contribution_score"]) / max(0.01, orig_f["contribution_score"])
            changed_features.append({
                "feature_name": fname,
                "original_contribution": orig_f["contribution_score"],
                "simulated_contribution": sim_f["contribution_score"],
                "impact": f"Reduced value drops contribution by {int(impact_diff * 100)}%" if impact_diff > 0 else f"Increased value raises contribution by {int(-impact_diff * 100)}%"
            })

    would_flag = sim_conf["overall_confidence"] >= 0.5 or sim_data.get("z_score", 0) >= 3.0

    return {
        "original_confidence": orig_conf["overall_confidence"],
        "simulated_confidence": sim_conf["overall_confidence"],
        "would_still_flag": would_flag,
        "changed_features": changed_features,
        "threshold_analysis": {
            "z_score_threshold": 3.0,
            "required_to_flag": 3.0,
            "current_simulated": round(sim_data.get("z_score", 0), 2)
        }
    }
