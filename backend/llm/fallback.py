"""
Fallback explanation generator for when LLM API is unavailable.

Provides rule-based templates to ensure explanations are always available.
"""

from __future__ import annotations


def generate_fallback_explanation(
    amount: float,
    merchant: str,
    z_score: float | None
) -> str:
    """
    Generate rule-based explanation when LLM is unavailable.
    
    Fallback template: ensures explanations always available even if LLM API fails
    
    Args:
        amount: Transaction amount
        merchant: Merchant name
        z_score: Statistical deviation score (None for duplicate anomalies)
    
    Returns:
        Template-based explanation string
    """
    # Fallback template: ensures explanations always available even if LLM API fails
    
    # Format amount with thousands separator
    formatted_amount = f"${amount:,.2f}"
    
    # Different templates based on anomaly type
    if z_score is not None:
        # Statistical anomaly template
        return (
            f"This {formatted_amount} charge to {merchant} is "
            f"{abs(z_score):.1f} standard deviations above your 6-month average."
        )
    else:
        # Duplicate anomaly template
        return f"This transaction appears to be a duplicate charge from {merchant}."
