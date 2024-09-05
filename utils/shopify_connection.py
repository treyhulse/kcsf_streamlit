import requests
import streamlit as st

# Function to get the Shopify connection headers
def get_shopify_headers():
    api_key = st.secrets['shopify_api_key']
    api_secret = st.secrets['shopify_api_secret']

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": api_key
    }
    
    return headers

# Function to test the connection by getting Shopify store information
def test_shopify_connection():
    shop_url = f"https://{st.secrets['shopify_store']}.myshopify.com/admin/api/2023-01/shop.json"
    
    headers = get_shopify_headers()
    
    response = requests.get(shop_url, headers=headers)
    
    if response.status_code == 200:
        st.success("Successfully connected to Shopify store!")
        return response.json()
    else:
        st.error(f"Failed to connect to Shopify. Status code: {response.status_code}")
        return None
