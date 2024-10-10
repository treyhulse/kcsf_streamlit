import streamlit as st
import requests
import base64
import datetime
import time

# Estes API URLs
AUTH_URL = "https://cloudapi.estes-express.com/authenticate"
QUOTE_URL = "https://cloudapi.estes-express.com/v1/rate-quotes"
TRACKING_URL = "https://cloudapi.estes-express.com/v1/shipments/history"
PICKUP_URL = "https://cloudapi.estes-express.com/v1/pickup-requests"

# Function to get a new Estes bearer token
def get_estes_bearer_token():
    api_key = st.secrets["ESTES_API_KEY"]
    username = st.secrets["ESTES_USERNAME"]
    password = st.secrets["ESTES_PASSWORD"]
    
    auth_string = f"{username}:{password}"
    auth_header_value = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'accept': 'application/json',
        'Authorization': f'Basic {auth_header_value}',
        'apikey': api_key
    }

    response = requests.post(AUTH_URL, headers=headers)
    
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token'], token_info['expires_in']  # Returns token and expiry in seconds
    else:
        st.error(f"Failed to get token: {response.status_code} - {response.text}")
        return None, None

# Function to manage Estes token retrieval/refresh
def get_valid_estes_token():
    # Check if the token is already in session state or if it has expired
    if 'estes_token' not in st.session_state or 'estes_token_expiration' not in st.session_state:
        # Request a new token if none exists
        new_token, expires_in = get_estes_bearer_token()
        if new_token:
            st.session_state['estes_token'] = new_token
            st.session_state['estes_token_expiration'] = time.time() + expires_in - 60  # Subtract 60 seconds for safety
    elif time.time() > st.session_state['estes_token_expiration']:
        # Refresh the token if it has expired
        new_token, expires_in = get_estes_bearer_token()
        if new_token:
            st.session_state['estes_token'] = new_token
            st.session_state['estes_token_expiration'] = time.time() + expires_in - 60  # Subtract 60 seconds for safety

    # Return the valid token
    return st.session_state.get('estes_token', None)

# Function to send rate quote request
def send_rate_quote_request(payload):
    token = get_valid_estes_token()
    if not token:
        st.error("Failed to retrieve a valid bearer token.")
        return

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }

    response = requests.post(QUOTE_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        st.success("Freight quote retrieved successfully!")
        st.json(response.json())
    else:
        st.error(f"Failed to retrieve freight quote: {response.status_code}")
        st.write(response.text)

# Streamlit UI components
st.title("Estes API Integration Tool")

st.sidebar.title("API Actions")
action = st.sidebar.selectbox(
    "Select an Action",
    ("Authenticate", "Get Rate Quote", "Track Shipment", "Create Pickup Request")
)

if action == "Authenticate":
    if st.button("Authenticate"):
        token = get_valid_estes_token()
        if token:
            st.success("Authentication successful.")
            st.sidebar.write(f"Bearer Token: {token}")

elif action == "Get Rate Quote":
    st.header("Get Rate Quote")
    shipper_zip = st.text_input("Shipper Zip Code")
    consignee_zip = st.text_input("Consignee Zip Code")
    weight = st.number_input("Total Weight (lbs)", min_value=1)
    total_pieces = st.number_input("Total Pieces", min_value=1)
    
    if st.button("Send Rate Quote Request"):
        quote_payload = {
            "shipper": {"postalCode": shipper_zip},
            "consignee": {"postalCode": consignee_zip},
            "totalWeight": weight,
            "totalPieces": total_pieces
        }
        send_rate_quote_request(quote_payload)

st.sidebar.write(f"Bearer Token: {st.session_state.get('estes_token', 'None')}")
