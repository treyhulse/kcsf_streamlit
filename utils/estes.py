import base64
import requests
import streamlit as st

# Estes API URLs
AUTH_URL = "https://cloudapi.estes-express.com/authenticate"
QUOTE_URL = "https://cloudapi.estes-express.com/v1/rate-quotes"

# Function to get a new bearer token with Basic Auth encoding
def get_bearer_token():
    # Load Estes API credentials from secrets
    api_key = st.secrets["ESTES_API_KEY"]
    username = st.secrets["ESTES_USERNAME"]
    password = st.secrets["ESTES_PASSWORD"]

    # Encode the username and password in Basic Auth format (Base64)
    auth_string = f"{username}:{password}"
    auth_header_value = base64.b64encode(auth_string.encode()).decode()

    # Set the headers, including the Authorization and API key
    headers = {
        'accept': 'application/json',
        'Authorization': f'Basic {auth_header_value}',
        'apikey': api_key
    }

    # Send the POST request to authenticate
    response = requests.post(AUTH_URL, headers=headers)

    # Check the response status and handle accordingly
    if response.status_code == 200:
        token = response.json().get('access_token')
        st.session_state["bearer_token"] = token  # Store the token in session state
        return token
    else:
        error_message = response.json().get('error', {}).get('message', 'Unknown error')
        st.error(f"Failed to authenticate: {error_message}")
        return None

# Function to get the current bearer token from session state or refresh if missing
def get_or_refresh_token():
    if "bearer_token" not in st.session_state:
        return get_bearer_token()  # Get a new token if not already in session state
    return st.session_state["bearer_token"]

# Function to request a freight quote using the current bearer token
def get_freight_quote(pickup_zip, delivery_zip, weight, handling_units):
    token = get_or_refresh_token()  # Ensure we have a valid token

    if token:
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'apikey': st.secrets["ESTES_API_KEY"]
        }

        # Set up the payload using the ESTES_ACCOUNT_ID from secrets and the ship date as "2024-11-20"
        payload = {
            "quoteRequest": {
                "shipDate": "2024-11-20",
                "shipTime": "16:00",
                "serviceLevels": ["LTL", "LTLTC"]
            },
            "payment": {
                "account": st.secrets["ESTES_ACCOUNT_ID"],  # Use ESTES_ACCOUNT_ID from secrets
                "payor": "Shipper",
                "terms": "Prepaid"
            },
            "origin": {
                "name": "ABC Origin Company",
                "locationId": "123",
                "address": {
                    "address1": "123 Busy Street",
                    "address2": "Suite A",
                    "city": "Washington",
                    "stateProvince": "DC",
                    "postalCode": "20001",
                    "country": "US"
                }
            },
            "destination": {
                "name": "XYZ Destination Company",
                "locationId": "987-B",
                "address": {
                    "address1": "456 Any Street",
                    "address2": "Door 2",
                    "city": "Richmond",
                    "stateProvince": "VA",
                    "postalCode": "23234",
                    "country": "US"
                }
            },
            "commodity": {
                "handlingUnits": [
                    {
                        "count": handling_units,
                        "type": "BX",
                        "weight": weight,
                        "weightUnit": "Pounds",
                        "dimensionsUnit": "Inches"
                    }
                ]
            }
        }

        response = requests.post(QUOTE_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to retrieve a freight quote: {response.json().get('error', {}).get('message', 'Unknown error')}")
            return None
    else:
        st.error("Bearer token is not available. Please refresh the token.")
        return None

# Function to manually refresh the token
def refresh_token():
    st.session_state["bearer_token"] = get_bearer_token()  # Refresh and store the new token
    if st.session_state["bearer_token"]:
        st.success("Bearer token refreshed successfully!")
    else:
        st.error("Failed to refresh bearer token.")
