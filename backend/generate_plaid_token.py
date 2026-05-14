"""
Generate Plaid Sandbox Access Token

Run this script once to get your access token for the sandbox environment.
"""

import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products

# INSTRUCTIONS:
# 1. Replace YOUR_CLIENT_ID and YOUR_SECRET below with your actual credentials
# 2. Run: python generate_plaid_token.py
# 3. Copy the access token it prints
# 4. Add it to your .env file as PLAID_ACCESS_TOKEN

# PASTE YOUR CREDENTIALS HERE:
PLAID_CLIENT_ID = "6a05b3f5826f25000d48d121"  # ← Replace with your actual client_id from Plaid dashboard
PLAID_SECRET = "620d59c00a144a3dd07ce474aa666c"        # ← Replace with your actual secret from Plaid dashboard

def generate_access_token():
    """Generate a sandbox access token."""
    
    # Initialize Plaid client
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': PLAID_CLIENT_ID,
            'secret': PLAID_SECRET,
        }
    )
    
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    
    print("Creating sandbox public token...")
    
    # Create sandbox public token with Chase bank
    request = SandboxPublicTokenCreateRequest(
        institution_id='ins_109508',  # Chase (sandbox)
        initial_products=[Products("transactions")]
    )
    
    try:
        response = client.sandbox_public_token_create(request)
        public_token = response['public_token']
        print(f"✓ Public token created: {public_token[:20]}...")
        
        # Exchange for access token
        print("Exchanging for access token...")
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        
        print("\n" + "="*60)
        print("SUCCESS! Your Plaid Access Token:")
        print("="*60)
        print(f"\n{access_token}\n")
        print("="*60)
        print("\nAdd this to your backend/.env file:")
        print(f"PLAID_ACCESS_TOKEN={access_token}")
        print("="*60)
        
        return access_token
        
    except plaid.ApiException as e:
        print(f"\n❌ Error: {e}")
        print(f"Status: {e.status}")
        print(f"Response: {e.body}")
        print("\nMake sure you replaced YOUR_CLIENT_ID and YOUR_SECRET with your actual credentials!")
        return None

if __name__ == "__main__":
    if PLAID_CLIENT_ID == "YOUR_CLIENT_ID" or PLAID_SECRET == "YOUR_SECRET":
        print("❌ ERROR: You need to replace YOUR_CLIENT_ID and YOUR_SECRET with your actual credentials!")
        print("\nEdit this file and replace:")
        print('  PLAID_CLIENT_ID = "YOUR_CLIENT_ID"')
        print('  PLAID_SECRET = "YOUR_SECRET"')
        print("\nWith your actual values from the Plaid dashboard.")
    else:
        generate_access_token()
