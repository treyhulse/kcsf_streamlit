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

# Function to handle token retrieval and refresh centrally
def get_valid_estes_token():
    # Check if the token exists and has not expired
    if 'estes_token' not in st.session_state or 'estes_token_expiration' not in st.session_state:
        # If no token or expiration information, retrieve a new one
        new_token, expires_in = get_estes_bearer_token()
        st.session_state['estes_token'] = new_token
        st.session_state['estes_token_expiration'] = time.time() + expires_in - 60  # Subtract 60 seconds as a buffer
    elif time.time() > st.session_state['estes_token_expiration']:
        # If the token has expired, retrieve a new one
        new_token, expires_in = get_estes_bearer_token()
        st.session_state['estes_token'] = new_token
        st.session_state['estes_token_expiration'] = time.time() + expires_in - 60

    # Return the current valid token
    return st.session_state['estes_token']

# Function to retrieve a new bearer token from the Estes API
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
        token_data = response.json()
        token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 3600)  # Default expiry to 3600 seconds if not specified
        st.session_state['estes_token'] = token  # Save the token immediately to session state
        st.session_state['estes_token_expiration'] = time.time() + expires_in - 60
        return token, expires_in
    else:
        error_message = response.json().get('error', {}).get('message', 'Unknown error')
        st.error(f"Failed to authenticate: {error_message}")
        raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

# Function to send a rate quote request to Estes API
def send_rate_quote_request(payload):
    # Get a valid token using the centralized function
    token = get_valid_estes_token()
    
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }
    response = requests.post(QUOTE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        st.success("Freight quote retrieved successfully!")
        return response.json()
    else:
        st.error(f"Failed to retrieve freight quote: {response.text}")
        return None

# Function to track a shipment using PRO number
def track_shipment(pro_number):
    # Get a valid token using the centralized function
    token = get_valid_estes_token()
    
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }
    params = {"pro": pro_number}
    response = requests.get(TRACKING_URL, headers=headers, params=params)
    if response.status_code == 200:
        st.success("Shipment tracking details retrieved successfully!")
        return response.json()
    else:
        st.error(f"Failed to retrieve shipment tracking details: {response.text}")
        return None

# Function to create a pickup request
def create_pickup_request(payload):
    # Get a valid token using the centralized function
    token = get_valid_estes_token()
    
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }
    response = requests.post(PICKUP_URL, headers=headers, json=payload)
    if response.status_code == 201:
        st.success("Pickup request created successfully!")
        return response.json()
    else:
        st.error(f"Failed to create pickup request: {response.text}")
        return None

# Streamlit UI components
st.title("Estes API Integration Tool")

# Sidebar to select actions
st.sidebar.title("API Actions")
action = st.sidebar.selectbox(
    "Select an Action",
    ("Authenticate", "Get Rate Quote", "Track Shipment", "Create Pickup Request")
)

# Display current bearer token in the sidebar if available
if 'estes_token' in st.session_state:
    st.sidebar.write(f"Current Bearer Token: {st.session_state['estes_token']}")
else:
    st.sidebar.write("No Bearer Token available.")

if action == "Authenticate":
    if st.button("Authenticate"):
        try:
            # Fetch or refresh the token and display it
            token = get_valid_estes_token()
            st.success("Authentication successful.")
            st.sidebar.write(f"Bearer Token: {token}")  # Update sidebar with new token
        except Exception as e:
            st.error(f"Authentication failed: {e}")

elif action == "Get Rate Quote":
    st.header("Get Rate Quote")
    # Placeholder fields for quote request payload
    shipper_zip = st.text_input("Shipper Zip Code")
    consignee_zip = st.text_input("Consignee Zip Code")
    weight = st.number_input("Total Weight (lbs)", min_value=1)
    total_pieces = st.number_input("Total Pieces", min_value=1)
    # Additional fields can be added as needed based on payload requirements
    if st.button("Send Rate Quote Request"):
        quote_payload = {
            "shipper": {"postalCode": shipper_zip},
            "consignee": {"postalCode": consignee_zip},
            "totalWeight": weight,
            "totalPieces": total_pieces
        }
        response = send_rate_quote_request(quote_payload)
        if response:
            st.json(response)

elif action == "Track Shipment":
    st.header("Track Shipment")
    pro_number = st.text_input("PRO Number")
    if st.button("Track Shipment"):
        response = track_shipment(pro_number)
        if response:
            st.json(response)

elif action == "Create Pickup Request":
    st.header("Create Pickup Request")
    # Placeholder fields for pickup request payload
    shipper_name = st.text_input("Shipper Name")
    account_code = st.text_input("Account Code")
    shipper_address = st.text_input("Shipper Address")
    pickup_date = st.date_input("Pickup Date")
    if st.button("Create Pickup Request"):
        pickup_payload = {
            "shipper": {
                "shipperName": shipper_name,
                "accountCode": account_code,
                "shipperAddress": {"addressInfo": {"addressLine1": shipper_address}},
            },
            "pickupDate": pickup_date.strftime("%Y-%m-%d")
        }
        response = create_pickup_request(pickup_payload)
        if response:
            st.json(response)

# Immediately display the current token state after a successful action
if 'estes_token' in st.session_state:
    st.sidebar.write(f"Updated Bearer Token: {st.session_state['estes_token']}")
else:
    st.sidebar.write("No Bearer Token available.")
