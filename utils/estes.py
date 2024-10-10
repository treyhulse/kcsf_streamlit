import streamlit as st
import requests
import base64

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

# Function to manually refresh the token
def refresh_token():
    token = get_bearer_token()
    if token:
        st.success("Bearer token refreshed successfully!")
    else:
        st.error("Failed to refresh bearer token.")

# Function to make a request to the rate-quotes endpoint using the stored bearer token
def send_rate_quote_request():
    # Get the token from session state
    if "bearer_token" not in st.session_state:
        st.error("No bearer token found. Please refresh the token first.")
        return

    token = st.session_state["bearer_token"]

    # Define headers with the bearer token
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }

    # Hardcoded sample request payload for testing
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
                    "count": 1,
                    "type": "BX",
                    "weight": 500,
                    "weightUnit": "Pounds",
                    "length": 48,
                    "width": 48,
                    "height": 48,
                    "dimensionsUnit": "Inches",
                    "isStackable": True,
                    "isTurnable": True
                }
            ]
        },
        "accessorials": {
            "codes": ["APT", "ULFEE"]
        }
    }

    # Send the POST request to the rate-quote endpoint
    response = requests.post(QUOTE_URL, headers=headers, json=payload)

    if response.status_code == 200:
        st.success("Freight quote retrieved successfully!")
        st.json(response.json())
    else:
        st.error(f"Failed to retrieve freight quote: {response.text}")

# UI Layout
st.title("Estes LTL Shipment Rate Generator (Simplified)")

# Display the current bearer token
st.write(f"Current Bearer Token: {st.session_state.get('bearer_token', 'None')}")

# Button to manually refresh bearer token
if st.button("Refresh Bearer Token"):
    refresh_token()

# Button to send the rate quote request using the stored bearer token
if st.button("Send Rate Quote Request"):
    send_rate_quote_request()
