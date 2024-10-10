import streamlit as st
import requests
import base64
import datetime

# Estes API URLs
AUTH_URL = "https://cloudapi.estes-express.com/authenticate"
QUOTE_URL = "https://cloudapi.estes-express.com/v1/rate-quotes"
TRACKING_URL = "https://cloudapi.estes-express.com/v1/shipments/history"
PICKUP_URL = "https://cloudapi.estes-express.com/v1/pickup-requests"

# Function to get bearer token
def get_bearer_token():
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
        expiry_seconds = token_data.get('expires_in', 3600)  # Default expiry time in seconds
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=expiry_seconds)
        st.session_state["bearer_token"] = token
        st.session_state["token_expiry"] = expiry_time
        st.success("Authentication successful.")
        return token
    else:
        error_message = response.json().get('error', {}).get('message', 'Unknown error')
        st.error(f"Failed to authenticate: {error_message}")
        return None

# Function to refresh token if needed
def refresh_token_if_needed():
    if "token_expiry" in st.session_state and st.session_state["token_expiry"] > datetime.datetime.now():
        return st.session_state["bearer_token"]
    else:
        return get_bearer_token()

# Function to send rate quote request
def send_rate_quote_request(payload):
    token = refresh_token_if_needed()
    if not token:
        st.error("No bearer token found or token expired. Attempting to refresh.")
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
        st.error(f"Failed to retrieve freight quote: {response.text}")

# Function to track shipment
def track_shipment(pro_number):
    token = refresh_token_if_needed()
    if not token:
        st.error("No bearer token found or token expired. Attempting to refresh.")
        return

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }
    params = {"pro": pro_number}
    response = requests.get(TRACKING_URL, headers=headers, params=params)
    if response.status_code == 200:
        st.success("Shipment tracking details retrieved successfully!")
        st.json(response.json())
    else:
        st.error(f"Failed to retrieve shipment tracking details: {response.text}")

# Function to create a pickup request
def create_pickup_request(payload):
    token = refresh_token_if_needed()
    if not token:
        st.error("No bearer token found or token expired. Attempting to refresh.")
        return

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }
    response = requests.post(PICKUP_URL, headers=headers, json=payload)
    if response.status_code == 201:
        st.success("Pickup request created successfully!")
        st.json(response.json())
    else:
        st.error(f"Failed to create pickup request: {response.text}")

# Streamlit UI components
st.title("Estes API Integration Tool")

st.sidebar.title("API Actions")
action = st.sidebar.selectbox(
    "Select an Action",
    ("Authenticate", "Get Rate Quote", "Track Shipment", "Create Pickup Request")
)

if action == "Authenticate":
    if st.button("Authenticate"):
        get_bearer_token()

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
        send_rate_quote_request(quote_payload)

elif action == "Track Shipment":
    st.header("Track Shipment")
    pro_number = st.text_input("PRO Number")
    if st.button("Track Shipment"):
        track_shipment(pro_number)

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
        create_pickup_request(pickup_payload)

st.sidebar.write(f"Current Bearer Token: {st.session_state.get('bearer_token', 'None')}")
