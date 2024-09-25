import streamlit as st
import requests
from requests_oauthlib import OAuth1

def get_netsuite_auth():
    """Authenticate using OAuth 1.0 with credentials from st.secrets"""
    consumer_key = st.secrets["consumer_key"]
    consumer_secret = st.secrets["consumer_secret"]
    token_key = st.secrets["token_key"]
    token_secret = st.secrets["token_secret"]

    return OAuth1(consumer_key, consumer_secret, token_key, token_secret)

def make_netsuite_request(url, params=None):
    """Make an authenticated GET request to NetSuite"""
    auth = get_netsuite_auth()
    response = requests.get(url, auth=auth, params=params)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch data: {response.status_code}")
        return None
    return response.json()
