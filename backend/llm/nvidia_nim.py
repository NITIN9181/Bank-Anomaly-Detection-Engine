"""
NVIDIA NIM LLM integration for anomaly explanations.

Uses dracarys-llama-3.1-70b-instruct via free endpoint for natural language generation.
"""

from __future__ import annotations

import logging

import httpx

from config import settings

# Configure logging
logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Custom exception for LLM API errors."""
    pass


async def generate_explanation(
    amount: float,
    merchant: str,
    mean: float,
    std: float,
    z_score: float
) -> str:
    """
    Generate natural language explanation for anomaly using NVIDIA NIM.
    
    NVIDIA NIM Free Endpoint: $0 cost, validated output quality with dracarys-llama-3.1-70b-instruct
    
    Args:
        amount: Transaction amount
        merchant: Merchant name
        mean: 6-month average for this vendor
        std: 6-month standard deviation
        z_score: Statistical deviation score
    
    Returns:
        Natural language explanation (1 sentence, <25 words)
    
    Raises:
        LLMError: If API call fails or returns invalid response
    """
    # NVIDIA NIM Free Endpoint: $0 cost, validated output quality with dracarys-llama-3.1-70b-instruct
    
    # Construct prompt with exact template from SPEC
    prompt = f"""You are a financial reconciliation assistant. 
Given the data below, explain in ONE concise sentence why this transaction is anomalous.
Do not speculate about fraud. Use only the facts provided.

Transaction: ${amount:.2f} to {merchant}
6-month average for this vendor: ${mean:.2f}
Standard deviation: ${std:.2f}
Z-score: {z_score:.2f}

Explanation:"""
    
    # API configuration
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_NIM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dracarys-llama-3.1-70b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 60,
        "top_p": 0.9
    }
    
    # Make async HTTP request with timeout
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            # Check HTTP status
            if response.status_code != 200:
                raise LLMError(f"NVIDIA NIM returned {response.status_code}")
            
            # Parse response
            try:
                data = response.json()
                explanation = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                raise LLMError(f"Invalid response format: {e}")
            
            # Clean and return
            explanation = explanation.strip()
            logger.info(f"Generated explanation: {explanation[:50]}...")
            
            return explanation
    
    except httpx.TimeoutException:
        logger.error("NVIDIA NIM request timed out")
        raise LLMError("Request timed out after 5 seconds")
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        raise LLMError(f"HTTP error: {e.response.status_code}")
