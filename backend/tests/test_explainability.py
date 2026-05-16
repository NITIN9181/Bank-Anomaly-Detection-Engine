import pytest
from backend.explainability.engine import calculate_feature_contributions
from backend.explainability.confidence import compute_confidence
from backend.explainability.recommender import get_recommended_actions
from backend.explainability.what_if import simulate_what_if

def test_calculate_feature_contributions():
    transaction = {"amount": 5000, "velocity_score": 5, "merchant_rarity": 0.3}
    vendor_profile = {"avg_amount": 100}
    
    contributions = calculate_feature_contributions(transaction, vendor_profile, 4.5, -0.4)
    
    # Check normalization
    total = sum(c["contribution_score"] for c in contributions)
    assert abs(total - 1.0) < 0.05
    
    # Check feature presence
    feature_names = [c["feature_name"] for c in contributions]
    assert "amount_deviation" in feature_names
    assert "ml_anomaly" in feature_names
    
def test_compute_confidence():
    tx_dict = {
        "z_score": 4.5,
        "isolation_score": -0.4,
        "is_duplicate": True
    }
    
    result = compute_confidence(tx_dict)
    
    assert "overall_confidence" in result
    assert "confidence_breakdown" in result
    assert result["overall_confidence"] > 0.8  # high confidence due to agreement
    assert result["confidence_breakdown"]["layer_agreement"] >= 0.1 # Should have agreement bonus

def test_get_recommended_actions():
    features = [
        {"feature_name": "amount_deviation", "contribution_score": 0.45, "value": 5000},
        {"feature_name": "velocity_cluster", "contribution_score": 0.20, "value": 5}
    ]
    actions = get_recommended_actions(features, 0.85, False)
    
    action_ids = [a["action_id"] for a in actions]
    assert "review_vendor" in action_ids
    assert actions[0]["priority"] == 1 # Highest priority first

def test_simulate_what_if():
    original_data = {
        "amount": 5000,
        "velocity_score": 5,
        "merchant_rarity": 0.3,
        "z_score": 4.5,
        "isolation_score": -0.4,
        "is_duplicate": False
    }
    vendor_profile = {"avg_amount": 100}
    
    # Simulate dropping amount
    sim_params = {"amount": 1000}
    result = simulate_what_if(original_data, vendor_profile, sim_params)
    
    assert result["original_confidence"] > result["simulated_confidence"]
    assert len(result["changed_features"]) > 0
