# In utils/rest.py

import json
import requests
from requests_oauthlib import OAuth1
import streamlit as st

def get_netsuite_auth():
    """Authenticate using OAuth 1.0 with credentials from st.secrets and include realm"""
    consumer_key = st.secrets["consumer_key"]
    consumer_secret = st.secrets["consumer_secret"]
    token_key = st.secrets["token_key"]
    token_secret = st.secrets["token_secret"]
    realm = st.secrets["realm"]

    # Include the realm in the OAuth1 header
    return OAuth1(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=token_key,
        resource_owner_secret=token_secret,
        realm=realm,
        signature_method='HMAC-SHA256'
    )

def make_netsuite_rest_api_request(url, payload=None, method="GET"):
    """Make an authenticated request to the NetSuite REST API with the specified method."""
    auth = get_netsuite_auth()
    rest_url = st.secrets["rest_url"]
    
    headers = {
        "Content-Type": "application/json",
    }

    # Convert payload to JSON if it's not None
    json_payload = None
    if payload:
        json_payload = json.dumps(payload)

    # Determine the HTTP method and send the request
    if method == "GET":
        response = requests.get(url, headers=headers, auth=auth)
    elif method == "POST":
        response = requests.post(url, headers=headers, auth=auth, data=json_payload)
    elif method == "PATCH":
        response = requests.patch(url, headers=headers, auth=auth, data=json_payload)
    elif method == "PUT":
        response = requests.put(url, headers=headers, auth=auth, data=json_payload)
    else:
        raise ValueError("Invalid HTTP method specified.")

    # Check for response status and content
    if response.status_code != 200:
        st.error(f"Failed to fetch data: {response.status_code}")
        st.write(f"Error content: {response.text}")
        return None

    return response.json()
