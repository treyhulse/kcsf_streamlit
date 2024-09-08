# utils/connections.py
from requests_oauthlib import OAuth1
import streamlit as st
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def get_authentication():
    """
    Create OAuth1 authentication object for NetSuite RESTlet calls.
    The credentials are fetched from Streamlit secrets.
    """
    try:
        # OAuth1 for NetSuite authentication
        auth = OAuth1(
            st.secrets["consumer_key"],
            st.secrets["consumer_secret"],
            st.secrets["token_key"],
            st.secrets["token_secret"],
            realm=st.secrets["realm"],
            signature_method='HMAC-SHA256'
        )
        logging.info("Successfully authenticated to NetSuite.")
        return auth
    except KeyError as e:
        logging.error(f"Missing secret: {e}")
        st.error(f"Missing secret: {e}")
        return None
