import requests
import streamlit as st

# Function to get the Shopify connection headers with the admin API key
def get_shopify_headers(use_admin_key=False):
    api_key = st.secrets['shopify_admin_api_key'] if use_admin_key else st.secrets['shopify_api_key']
    
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": api_key
    }
    
    return headers

# Function to test the connection by getting Shopify store information
def test_shopify_connection():
    shop_url = f"https://{st.secrets['shopify_store']}.myshopify.com/admin/api/2023-01/shop.json"
    
    headers = get_shopify_headers(use_admin_key=True)  # You can choose to use the admin key here
    
    response = requests.get(shop_url, headers=headers)
    
    if response.status_code == 200:
        st.success("Successfully connected to Shopify store!")
        return response.json()
    else:
        st.error(f"Failed to connect to Shopify. Status code: {response.status_code}")
        return None
