"""
Anomaly explanation orchestrator.

Coordinates LLM explanation generation with fallback and caching.
"""

from __future__ import annotations

import logging

import httpx
from sqlalchemy.orm import Session

from database.models import Anomaly, Transaction, VendorProfile
from llm.fallback import generate_fallback_explanation
from llm.nvidia_nim import LLMError, generate_explanation

# Configure logging
logger = logging.getLogger(__name__)


async def explain_anomaly(anomaly_id: int, db: Session) -> str:
    """
    Generate or retrieve explanation for an anomaly.
    
    Cache explanations in DB to avoid re-calling LLM for same anomaly
    
    Workflow:
    1. Check if explanation already cached in database
    2. Try NVIDIA NIM LLM for natural language generation
    3. Fall back to rule-based template if LLM fails
    4. Cache result in database
    
    Args:
        anomaly_id: ID of anomaly to explain
        db: Database session
    
    Returns:
        Natural language explanation string
    
    Raises:
        ValueError: If anomaly not found
    """
    # Cache explanations in DB to avoid re-calling LLM for same anomaly
    
    # Query anomaly
    anomaly = db.query(Anomaly).get(anomaly_id)
    if anomaly is None:
        raise ValueError(f"Anomaly {anomaly_id} not found")
    
    # Return cached explanation if available
    if anomaly.explanation and anomaly.explanation.strip():
        logger.info(f"Using cached explanation for anomaly {anomaly_id}")
        return anomaly.explanation
    
    # Get associated transaction
    transaction = db.query(Transaction).get(anomaly.transaction_id)
    if transaction is None:
        raise ValueError(f"Transaction {anomaly.transaction_id} not found")
    
    # Get vendor profile for context
    profile = None
    if transaction.merchant_name:
        profile = db.query(VendorProfile).filter(
            VendorProfile.merchant_name == transaction.merchant_name
        ).first()
    
    # Prepare data for explanation
    merchant_name = transaction.merchant_name or "Unknown"
    mean = profile.avg_amount if profile else 0.0
    std = profile.std_amount if profile else 0.0
    z_score = anomaly.z_score if anomaly.z_score else 0.0
    
    # Try NVIDIA NIM LLM first
    explanation = None
    try:
        if profile is not None:
            explanation = await generate_explanation(
                amount=transaction.amount,
                merchant=merchant_name,
                mean=mean,
                std=std,
                z_score=z_score
            )
            logger.info(f"LLM explanation generated for anomaly {anomaly_id}")
        else:
            # No profile available, use fallback immediately
            logger.info(f"No vendor profile for anomaly {anomaly_id}, using fallback")
            explanation = generate_fallback_explanation(
                amount=transaction.amount,
                merchant=merchant_name,
                z_score=anomaly.z_score
            )
    
    except (httpx.TimeoutException, httpx.HTTPStatusError, LLMError) as e:
        # LLM failed, use fallback template
        logger.warning(f"LLM failed for anomaly {anomaly_id}: {e}")
        explanation = generate_fallback_explanation(
            amount=transaction.amount,
            merchant=merchant_name,
            z_score=anomaly.z_score
        )
        logger.info(f"Fallback explanation generated for anomaly {anomaly_id}")
    
    # Cache explanation in database
    anomaly.explanation = explanation
    db.commit()
    
    return explanation


async def explain_all_new_anomalies(db: Session) -> int:
    """
    Generate explanations for all anomalies without explanations.
    
    Args:
        db: Database session
    
    Returns:
        Count of anomalies that received explanations
    """
    # Find anomalies without explanations (None or empty string)
    anomalies = db.query(Anomaly).filter(
        (Anomaly.explanation.is_(None)) | (Anomaly.explanation == "")
    ).all()
    
    if not anomalies:
        logger.info("No anomalies need explanations")
        return 0
    
    logger.info(f"Generating explanations for {len(anomalies)} anomalies")
    
    # Generate explanation for each
    explained_count = 0
    for anomaly in anomalies:
        try:
            await explain_anomaly(anomaly.id, db)
            explained_count += 1
        except Exception as e:
            logger.error(f"Failed to explain anomaly {anomaly.id}: {e}")
    
    logger.info(f"Successfully explained {explained_count}/{len(anomalies)} anomalies")
    return explained_count
