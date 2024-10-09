import requests
import streamlit as st

# Estes API URLs
AUTH_URL = "https://cloudapi.estes-express.com/authenticate"

# Authenticate and get bearer token
def get_bearer_token():
    # Load the API credentials from Streamlit secrets
    api_key = st.secrets["ESTES_API_KEY"]
    username = st.secrets["ESTES_USERNAME"]
    password = st.secrets["ESTES_PASSWORD"]

    headers = {
        'accept': 'application/json',
        'apikey': api_key
    }

    response = requests.post(AUTH_URL, headers=headers, auth=(username, password))
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        st.error(f"Failed to authenticate: {response.text}")
        return None

# Function to get freight quote
def get_freight_quote(token, pickup_zip, delivery_zip, weight, handling_units):
    QUOTE_URL = "https://cloudapi.estes-express.com/v1/rates"

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }

    payload = {
        "pickupLocation": {
            "postalCode": pickup_zip
        },
        "deliveryLocation": {
            "postalCode": delivery_zip
        },
        "commodities": [
            {
                "description": "Freight",
                "weight": weight,
                "handlingUnits": handling_units,
                "dimensions": {
                    "length": 48,
                    "width": 48,
                    "height": 40
                }
            }
        ],
        "accessorials": []
    }

    response = requests.post(QUOTE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to retrieve a freight quote: {response.text}")
        return None
