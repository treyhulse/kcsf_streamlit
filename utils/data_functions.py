import requests
import json
import streamlit as st
from requests_oauthlib import OAuth1

# Function to get saved search data from NetSuite
def get_saved_search_data():
    url = st.secrets['url_open_so']  # Use 'url_open_so' for the RESTlet URL
    consumer_key = st.secrets['consumer_key']
    consumer_secret = st.secrets['consumer_secret']
    token_key = st.secrets['token_key']
    token_secret = st.secrets['token_secret']

    # OAuth1 authentication
    auth = OAuth1(consumer_key, consumer_secret, token_key, token_secret)

    # Make GET request to the RESTlet
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return None
