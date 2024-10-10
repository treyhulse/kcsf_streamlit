import streamlit as st
import requests
import base64
import datetime

# Estes API URLs
AUTH_URL = "https://cloudapi.estes-express.com/authenticate"
QUOTE_URL = "https://cloudapi.estes-express.com/v1/rate-quotes"

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
        return token
    else:
        error_message = response.json().get('error', {}).get('message', 'Unknown error')
        st.error(f"Failed to authenticate: {error_message}")
        return None

def refresh_token_if_needed():
    if "token_expiry" in st.session_state and st.session_state["token_expiry"] > datetime.datetime.now():
        return st.session_state["bearer_token"]
    else:
        return get_bearer_token()

def send_rate_quote_request():
    token = refresh_token_if_needed()
    if not token:
        st.error("No bearer token found or token expired. Attempting to refresh.")
        return

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'apikey': st.secrets["ESTES_API_KEY"]
    }
    payload = {
        # Your payload here
    }
    response = requests.post(QUOTE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        st.success("Freight quote retrieved successfully!")
        st.json(response.json())
    else:
        st.error(f"Failed to retrieve freight quote: {response.text}")

st.title("Estes LTL Shipment Rate Generator (Enhanced)")

if st.button("Refresh Bearer Token"):
    get_bearer_token()
    st.write(f"Token refreshed. New Token: {st.session_state.get('bearer_token', 'None')}")

if st.button("Send Rate Quote Request"):
    send_rate_quote_request()

st.write(f"Current Bearer Token: {st.session_state.get('bearer_token', 'None')}")
