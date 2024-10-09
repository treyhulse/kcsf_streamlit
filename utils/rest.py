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
    """Make an authenticated request to the NetSuite REST API without returning a response."""
    auth = get_netsuite_auth()
    headers = {"Content-Type": "application/json"}

    # Convert payload to JSON if provided
    json_payload = json.dumps(payload) if payload else None

    try:
        # Determine the HTTP method and send the request
        if method == "PATCH":
            requests.patch(url, headers=headers, auth=auth, data=json_payload)
        elif method == "POST":
            requests.post(url, headers=headers, auth=auth, data=json_payload)
        elif method == "PUT":
            requests.put(url, headers=headers, auth=auth, data=json_payload)
        elif method == "DELETE":
            requests.delete(url, headers=headers, auth=auth)
        else:
            requests.get(url, headers=headers, auth=auth)
    except requests.exceptions.RequestException as e:
        # Raise the exception if any error occurs during the request
        raise e
