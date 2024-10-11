import requests
import streamlit as st
import base64

# Utility function to retrieve the API key, username, and password from st.secrets
def get_credentials():
    api_key = st.secrets["ESTES_API_KEY"]
    username = st.secrets["ESTES_USERNAME"]
    password = st.secrets["ESTES_PASSWORD"]
    return api_key, username, password

def get_bearer_token():
    """
    Function to retrieve a new bearer token using the stored API key, username, and password.
    The token will be stored in session state.
    """
    api_key, username, password = get_credentials()
    auth_string = f"{username}:{password}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    url = "https://cloudapi.estes-express.com/authenticate"
    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {encoded_auth}",
        "apikey": api_key
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        token = response.json().get("token", "No token found")
        st.session_state.bearer_token = token
        return token
    else:
        st.error(f"Failed to retrieve bearer token. Status code: {response.status_code}. Message: {response.text}")
        return None

def check_and_get_bearer_token():
    """
    Check if a bearer token exists in the session state. If not, retrieve a new one.
    """
    if "bearer_token" in st.session_state and st.session_state.bearer_token:
        return st.session_state.bearer_token
    else:
        return get_bearer_token()
