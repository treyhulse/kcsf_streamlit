import requests
import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Define the function to retrieve a new bearer token from FedEx using the updated secret names
def get_fedex_bearer_token():
    url = "https://apis.fedex.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": st.secrets["fedex_id"],          # Updated to use fedex_id from st.secrets
        "client_secret": st.secrets["fedex_secret"],  # Updated to use fedex_secret from st.secrets
    }

    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        token_info = response.json()
        # Return the token and its expiration time in seconds
        return token_info['access_token'], token_info['expires_in']
    else:
        raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

# Store the token in Streamlit session state
def update_token_in_session():
    # Check if the token is already in session state or has expired
    if 'fedex_token' not in st.session_state or 'fedex_token_expiration' not in st.session_state:
        # If no token exists in session or it has expired, request a new one
        new_token, expires_in = get_fedex_bearer_token()
        st.session_state['fedex_token'] = new_token
        st.session_state['fedex_token_expiration'] = time.time() + expires_in - 60  # Subtract 60 seconds for a safety margin
    elif time.time() > st.session_state['fedex_token_expiration']:
        # If the token has expired, refresh it
        new_token, expires_in = get_fedex_bearer_token()
        st.session_state['fedex_token'] = new_token
        st.session_state['fedex_token_expiration'] = time.time() + expires_in - 60  # Subtract 60 seconds for a safety margin

# Auto-refresh every 59 minutes to keep the token updated
st_autorefresh(interval=59*60*1000, key="refresh_token")

# Update token at the start of the application
update_token_in_session()
