from typing import Dict, Any
from explainability.confidence import compute_confidence
from explainability.engine import calculate_feature_contributions

def simulate_what_if(original_data: Dict[str, Any], vendor_profile: Dict[str, Any], sim_params: Dict[str, float]) -> Dict[str, Any]:
    """
    Accepts hypothetical feature values, re-runs detection math, 
    and returns whether anomaly would still flag + new confidence.
    """
    # Clone original data
    sim_data = original_data.copy()
    
    # Apply simulated params and recalculate z-score
    if "amount" in sim_params:
        sim_data["amount"] = sim_params["amount"]
        # Recalculate z-score based on new amount
        baseline_amount = vendor_profile.get("avg_amount", 100.0)
        # Assume std dev is 20% of baseline for simulation
        std_dev = baseline_amount * 0.2
        if std_dev > 0:
            sim_data["z_score"] = (sim_params["amount"] - baseline_amount) / std_dev
        else:
            sim_data["z_score"] = 0.0

    if "velocity" in sim_params:
        sim_data["velocity_score"] = sim_params["velocity"]
        
    # Re-calculate confidence with new values
    orig_conf = compute_confidence(original_data)
    sim_conf = compute_confidence(sim_data)
    
    # Re-calculate features with new values
    orig_feats = calculate_feature_contributions(
        original_data, 
        vendor_profile, 
        original_data.get("z_score", 0), 
        original_data.get("isolation_score", 0)
    )
    sim_feats = calculate_feature_contributions(
        sim_data, 
        vendor_profile, 
        sim_data.get("z_score", 0), 
        sim_data.get("isolation_score", 0)
    )
    
    changed_features = []
    
    orig_feat_map = {f["feature_name"]: f for f in orig_feats}
    sim_feat_map = {f["feature_name"]: f for f in sim_feats}
    
    # Compare all features
    all_feature_names = set(orig_feat_map.keys()) | set(sim_feat_map.keys())
    
    for fname in all_feature_names:
        orig_f = orig_feat_map.get(fname)
        sim_f = sim_feat_map.get(fname)
        
        orig_contrib = orig_f["contribution_score"] if orig_f else 0.0
        sim_contrib = sim_f["contribution_score"] if sim_f else 0.0
        
        if abs(sim_contrib - orig_contrib) > 0.01:
            change_pct = ((sim_contrib - orig_contrib) / max(0.01, orig_contrib)) * 100
            
            if change_pct > 0:
                impact = f"Increased by {abs(change_pct):.0f}%"
            else:
                impact = f"Decreased by {abs(change_pct):.0f}%"
                
            changed_features.append({
                "feature_name": fname,
                "original_contribution": round(orig_contrib, 2),
                "simulated_contribution": round(sim_contrib, 2),
                "impact": impact
            })

    # Determine if would still flag
    would_flag = (
        sim_conf["overall_confidence"] >= 0.5 or 
        abs(sim_data.get("z_score", 0)) >= 3.0 or
        sim_data.get("isolation_score", 0) <= -0.15
    )

    return {
        "original_confidence": orig_conf["overall_confidence"],
        "simulated_confidence": sim_conf["overall_confidence"],
        "would_still_flag": would_flag,
        "changed_features": sorted(changed_features, key=lambda x: abs(x["simulated_contribution"] - x["original_contribution"]), reverse=True),
        "threshold_analysis": {
            "z_score_threshold": 3.0,
            "required_to_flag": 3.0,
            "current_simulated": round(sim_data.get("z_score", 0), 2),
            "original_z_score": round(original_data.get("z_score", 0), 2)
        }
    }
