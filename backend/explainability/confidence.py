import math

def compute_confidence(detection_results: dict) -> dict:
    """
    Computes confidence score based on detection layer agreement.
    Returns overall confidence and layer breakdown.
    """
    z_score = detection_results.get("z_score", 0)
    isolation_score = detection_results.get("isolation_score", 0)
    duplicate_found = detection_results.get("is_duplicate", False)
    
    stat_triggered = abs(z_score) >= 3.0
    # Isolation score threshold assumption: -0.15
    ml_triggered = isolation_score <= -0.15
    dup_triggered = bool(duplicate_found)

    # Statistical layer confidence: sigmoid of z_score
    stat_conf = min(0.99, 1 / (1 + math.exp(-(abs(z_score) - 3))))
    
    # ML layer confidence: based on isolation score distance from threshold
    ml_conf = min(0.99, abs(isolation_score - (-0.15)) / 0.5)
    
    # Duplicate layer: binary 0 or 1
    dup_conf = 1.0 if dup_triggered else 0.0
    
    # Overall: weighted average with layer agreement bonus
    layers_triggered = sum([stat_triggered, ml_triggered, dup_triggered])
    if layers_triggered > 1:
        agreement_bonus = 0.1 * layers_triggered
    else:
        agreement_bonus = 0
    
    overall = (0.4 * stat_conf) + (0.4 * ml_conf) + (0.2 * dup_conf) + agreement_bonus
    overall = min(0.99, overall)
    
    return {
        "overall_confidence": round(overall, 2),
        "confidence_breakdown": {
            "statistical_layer": round(stat_conf, 2),
            "ml_layer": round(ml_conf, 2),
            "duplicate_layer": round(dup_conf, 2),
            "layer_agreement": round(min(0.99, layers_triggered * 0.33), 2)
        }
    }
