# utils/connections.py
import requests
import streamlit as st

# NetSuite Connection
def connect_to_netsuite():
    headers = {
        "Authorization": f"OAuth oauth_consumer_key={st.secrets['consumer_key']}, "
                         f"oauth_token={st.secrets['token_key']}, "
                         f"oauth_signature_method=HMAC-SHA256, "
                         f"oauth_signature={st.secrets['consumer_secret']}&{st.secrets['token_secret']}",
                         
        "Content-Type": "application/json"
    }
    netsuite_base_url = st.secrets['netsuite_base_url']
    return netsuite_base_url, headers

# Shopify Connection
def connect_to_shopify(use_admin_key=False):
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
    return shopify_url, headers
