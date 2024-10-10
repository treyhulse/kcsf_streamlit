# estes_refresh.py

import base64
import requests
import streamlit as st

# Estes API URL
ESTES_AUTH_URL = "https://cloudapi.estes-express.com/authenticate"  # Production URL

def get_bearer_token():
    """
    Retrieves a new bearer token from Estes API using username, password, and API key.
    
    Returns:
        str: The bearer token if the request is successful, else None.
    """
    # Retrieve credentials from Streamlit secrets
    estes_username = st.secrets["ESTES_USERNAME"]
    estes_password = st.secrets["ESTES_PASSWORD"]
    api_key = st.secrets["ESTES_API_KEY"]
    
    # Encode username and password in base64 for the Authorization header
    auth_str = f"{estes_username}:{estes_password}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    # Headers for the request
    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {encoded_auth}",
        "APIKEY": api_key,
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
