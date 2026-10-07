import os
import requests
from dotenv import load_dotenv 
from decimal import Decimal 

load_dotenv()

FLW_SECRET_KEY = os.environ['FLUTTERWAVE_SECRET_KEY']
BASE_URL = "https://api.flutterwave.com/v3"



def initiate_transaction(
        tx_ref: str,
        amount: Decimal,
        currency: str,
        email: str,
        redirect_url: str,
) -> dict:

    """Ask Flutterwave to create a payment session, returns their response including a checkout link."""

    headers = {"Authorization": f"Bearer {FLW_SECRET_KEY}"}
    payload = {
        "tx_ref": tx_ref,
        "amount": str(amount),
        "currency": currency,
        "redirect_url": redirect_url,
        "customer": {"email": email},
    }

    response = requests.post(f"{BASE_URL}/payments", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def verify_transaction(transaction_id: str) -> dict:

    """Ask Flutterwave directly: what is the real, current status of this transaction?"""
    
    headers = {"Authorization": f"Bearer {FLW_SECRET_KEY}"}
    response = requests.get(f"{BASE_URL}/transactions/{transaction_id}/verify", headers=headers)
    response.raise_for_status()
    return response.json()