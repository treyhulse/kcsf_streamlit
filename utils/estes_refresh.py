# estes_refresh.py

import requests
import base64
import streamlit as st

# Estes API URL
ESTES_AUTH_URL = "https://cloudapi.estes-express.com/authenticate"  # Production URL

def get_bearer_token():
    """
    Retrieves a new bearer token from Estes API using client credentials and API key.
    
    Returns:
        str: The bearer token if the request is successful, else None.
    """
    # Retrieve credentials from Streamlit secrets
    client_id = st.secrets["ESTES_CLIENT_ID"]
    client_secret = st.secrets["ESTES_CLIENT_SECRET"]
    api_key = st.secrets["ESTES_API_KEY"]
    
    # Encode client credentials in base64 for the Authorization header
    auth_str = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    # Headers for the request
    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {encoded_auth}",
        "apikey": api_key,
    }

    # Make a POST request to get the bearer token
    try:
        response = requests.post(ESTES_AUTH_URL, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")  # Extract the token from the response
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request exception occurred: {e}")
    return None
