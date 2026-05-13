"""
Statistical anomaly detection using rolling Z-score.

Provides interpretable threshold-based detection for clear deviations from vendor baselines.
"""

from __future__ import annotations

from typing import Any

from database.models import Transaction, VendorProfile


def detect_statistical_anomaly(
    transaction: Transaction,
    profile: VendorProfile | None
) -> dict[str, Any] | None:
    """
    Detect volumetric anomalies using Z-score threshold.
    
    Statistical layer provides interpretable threshold-based detection for clear deviations.
    A transaction is flagged if it deviates more than 3 standard deviations from the
    vendor's 6-month rolling average.
    
    Args:
        transaction: Transaction to evaluate
        profile: Vendor profile with historical statistics (may be None)
    
    Returns:
        Dictionary with anomaly type and z_score if anomalous, None otherwise
        Format: {"type": "volumetric", "z_score": float}
    """
    # Statistical layer: interpretable threshold-based detection. Z-score > 3.0 covers 99.7% of normal distribution.
    
    # Require minimum sample size for statistical validity
    if profile is None or profile.transaction_count < 5:
        return None
    
    # Handle missing or zero standard deviation
    if profile.std_amount is None or profile.std_amount == 0.0:
        return None
    
    # Handle missing average
    if profile.avg_amount is None:
        return None
    
    # Calculate Z-score: (observed - mean) / std
    z_score = (transaction.amount - profile.avg_amount) / profile.std_amount
    
    # Flag if absolute deviation exceeds 3 standard deviations (99.7% confidence)
    if abs(z_score) > 3.0:
        return {
            "type": "volumetric",
            "z_score": round(z_score, 2)
        }
    
    return None
