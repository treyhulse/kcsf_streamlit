# utils/connections.py
import requests
import streamlit as st
import logging
from requests_oauthlib import OAuth1

# Setup logging for better tracking
logging.basicConfig(level=logging.INFO)

# Set up logging for better tracking
logging.basicConfig(level=logging.INFO)

# NetSuite Connection
def get_authentication():
    """Get OAuth1 authentication for NetSuite requests."""
    try:
        return OAuth1(
            st.secrets["consumer_key"],
            st.secrets["consumer_secret"],
            st.secrets["token_key"],
            st.secrets["token_secret"],
            realm=st.secrets["realm"],
            signature_method='HMAC-SHA256'
        )
    except KeyError as e:
        logging.error(f"Missing secret: {e}")
        st.error(f"Missing secret: {e}")
        return None


# Shopify Connection
def connect_to_shopify(use_admin_key=False):
    try:
        if use_admin_key:
            api_key = st.secrets['shopify_admin_api_key']
        else:
            api_key = st.secrets['shopify_api_key']

        shopify_store = st.secrets['shopify_store']
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": api_key
        }
        shopify_url = f"https://{shopify_store}.myshopify.com/admin/api/2023-01/"
        logging.info("Shopify connection successful.")
        return shopify_url, headers
    except KeyError as e:
        logging.error(f"Missing secret: {e}")
        st.error(f"Missing secret: {e}")
        return None, None
