import requests
from requests_oauthlib import OAuth1
import streamlit as st

def get_netsuite_auth():
    """Authenticate using OAuth 1.0 with credentials from st.secrets"""
    consumer_key = st.secrets["consumer_key"]
    consumer_secret = st.secrets["consumer_secret"]
    token_key = st.secrets["token_key"]
    token_secret = st.secrets["token_secret"]

    return OAuth1(consumer_key, consumer_secret, token_key, token_secret, signature_method='HMAC-SHA256')

def make_netsuite_rest_api_request(endpoint):
    """Make an authenticated GET request to the NetSuite REST API"""
    auth = get_netsuite_auth()
    rest_url = st.secrets["rest_url"]
    
    # Construct the full URL for the request
    url = f"{rest_url}{endpoint}"
    response = requests.get(url, auth=auth)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch data: {response.status_code}")
        st.write(f"Error content: {response.text}")
        return None
    return response.json()
