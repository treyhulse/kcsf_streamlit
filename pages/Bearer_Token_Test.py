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

# Create a simple UI for testing
st.title("FedEx Bearer Token Test Page")

# Display the current token and expiration time
if 'fedex_token' in st.session_state and 'fedex_token_expiration' in st.session_state:
    st.subheader("Current Bearer Token")
    st.code(st.session_state['fedex_token'], language='plaintext')

    # Calculate remaining time until the token expires
    remaining_time = int(st.session_state['fedex_token_expiration'] - time.time())
    st.write(f"Token Expires In: {remaining_time} seconds")

    # Button to force refresh the token
    if st.button("Force Refresh Token"):
        update_token_in_session()
        st.success("Token refreshed successfully!")

# Button to check the validity of the current token
if st.button("Check Token Validity"):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state['fedex_token']}",
            "Content-Type": "application/json"
        }

        # Make a simple request to a FedEx API endpoint to check if the token works (you can replace this with your endpoint)
        fedex_api_url = "https://apis.fedex.com/rate/v1/rates/quotes"  # Replace with a valid endpoint if needed
        response = requests.get(fedex_api_url, headers=headers)

        if response.status_code == 200:
            st.success("Token is valid and working!")
        else:
            st.error(f"Token validation failed: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
