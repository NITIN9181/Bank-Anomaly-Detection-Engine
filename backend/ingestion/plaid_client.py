"""
Plaid API client for fetching banking transactions.

Handles authentication, pagination, retries, and error handling for Plaid Sandbox API.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

from config import settings

# Configure logging
logger = logging.getLogger(__name__)


class PlaidClient:
    """
    Client for interacting with Plaid Sandbox API.
    
    Attributes:
        client: Plaid API client instance
        access_token: Plaid access token for sandbox account
    """
    
    def __init__(self) -> None:
        """Initialize Plaid API client with credentials from settings."""
        configuration = plaid.Configuration(
            host=self._get_plaid_host(),
            api_key={
                "clientId": settings.PLAID_CLIENT_ID,
                "secret": settings.PLAID_SECRET,
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        
        # For sandbox, we'll need to create a link token and exchange it
        # In production, this would come from user OAuth flow
        # For now, we'll use a pre-configured sandbox access token
        # This should be set via environment variable in production
        self.access_token: str | None = None
        
        logger.info(f"Plaid client initialized for environment: {settings.PLAID_ENV}")
    
    def _get_plaid_host(self) -> str:
        """Get Plaid API host URL based on environment."""
        env_hosts = {
            "sandbox": plaid.Environment.Sandbox,
            "development": plaid.Environment.Development,
            "production": plaid.Environment.Production,
        }
        return env_hosts.get(settings.PLAID_ENV, plaid.Environment.Sandbox)
    
    def set_access_token(self, access_token: str) -> None:
        """
        Set the Plaid access token for API calls.
        
        Args:
            access_token: Plaid access token obtained from link flow
        """
        self.access_token = access_token
        logger.info("Plaid access token configured")
    
    def get_transactions(
        self,
        start_date: str,
        end_date: str,
        max_retries: int = 3
    ) -> list[dict[str, Any]]:
        """
        Fetch transactions from Plaid API with pagination and retry logic.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            max_retries: Maximum number of retry attempts on failure
        
        Returns:
            List of transaction dictionaries with normalized keys
        
        Raises:
            ValueError: If access token is not set
            Exception: If all retry attempts fail
        """
        if not self.access_token:
            raise ValueError("Access token not set. Call set_access_token() first.")
        
        all_transactions: list[dict[str, Any]] = []
        offset = 0
        total_transactions = None
        
        logger.info(f"Fetching transactions from {start_date} to {end_date}")
        
        while total_transactions is None or offset < total_transactions:
            for attempt in range(max_retries):
                try:
                    # Create request with pagination
                    request = TransactionsGetRequest(
                        access_token=self.access_token,
                        start_date=start_date,
                        end_date=end_date,
                        options=TransactionsGetRequestOptions(
                            count=500,  # Max per request
                            offset=offset
                        )
                    )
                    
                    # Make API call
                    response = self.client.transactions_get(request)
                    
                    # Extract transactions
                    transactions = response["transactions"]
                    total_transactions = response["total_transactions"]
                    
                    # Normalize transaction data
                    for txn in transactions:
                        normalized = self._normalize_transaction(txn)
                        all_transactions.append(normalized)
                    
                    # Update offset for next page
                    offset += len(transactions)
                    
                    logger.info(
                        f"Fetched {len(transactions)} transactions "
                        f"(total: {len(all_transactions)}/{total_transactions})"
                    )
                    
                    # Success - break retry loop
                    break
                    
                except plaid.ApiException as e:
                    logger.error(
                        f"Plaid API error (attempt {attempt + 1}/{max_retries}): "
                        f"Status {e.status}, Body: {e.body}"
                    )
                    
                    if attempt < max_retries - 1:
                        # Exponential backoff: 1s, 2s, 4s
                        sleep_time = 2 ** attempt
                        logger.info(f"Retrying in {sleep_time} seconds...")
                        time.sleep(sleep_time)
                    else:
                        logger.error("Max retries exceeded. Raising exception.")
                        raise
                
                except Exception as e:
                    logger.error(
                        f"Unexpected error (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** attempt
                        time.sleep(sleep_time)
                    else:
                        raise
        
        logger.info(f"Successfully fetched {len(all_transactions)} total transactions")
        return all_transactions
    
    def _normalize_transaction(self, txn: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize Plaid transaction data to internal format.
        
        Args:
            txn: Raw transaction dictionary from Plaid API
        
        Returns:
            Normalized transaction dictionary
        """
        # Extract merchant name (may be None for some transactions)
        merchant_name = None
        if txn.get("merchant_name"):
            merchant_name = txn["merchant_name"]
        elif txn.get("name"):
            merchant_name = txn["name"]
        
        # Normalize merchant name: strip whitespace and title-case
        if merchant_name:
            merchant_name = merchant_name.strip().title()
        
        # Extract category (Plaid returns list, take first)
        category = None
        if txn.get("category") and len(txn["category"]) > 0:
            category = txn["category"][0]
        
        return {
            "transaction_id": txn["transaction_id"],
            "account_id": txn["account_id"],
            "amount": float(txn["amount"]),  # Positive for debits, negative for credits
            "date": txn["date"],  # Already in YYYY-MM-DD format
            "merchant_name": merchant_name,
            "category": category,
        }


# Global client instance
plaid_client = PlaidClient()
