# shopify_connection.py

import requests
import streamlit as st

# Function to get the Shopify connection headers
def get_shopify_headers(use_admin_key=False):
    """
    Retrieves the appropriate Shopify API headers.
    
    Parameters:
        use_admin_key (bool): Whether to use the admin API key.
    
    Returns:
        dict: Headers for Shopify API requests.
    """
    if use_admin_key:
        api_key = st.secrets['shopify_admin_api_key']
    else:
        api_key = st.secrets['shopify_api_key']
    
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": api_key
    }
    
    return headers

# Function to test the connection by getting Shopify store information
def test_shopify_connection():
    """
    Tests the connection to the Shopify store.
    
    Returns:
        dict or None: Shop information if successful, None otherwise.
    """
    try:
        # Build the shop URL from the secrets
        shop_url = f"https://{st.secrets['shopify_store']}.myshopify.com/admin/api/2023-01/shop.json"
        
        # Get headers using admin API key
        headers = get_shopify_headers(use_admin_key=True)
        
        # Make a request to Shopify API
        response = requests.get(shop_url, headers=headers)
        
        # Check response status
        if response.status_code == 200:
            st.success("Successfully connected to Shopify store!")
            return response.json()  # Return the shop information in JSON format
        else:
            st.error(f"Failed to connect to Shopify. Status Code: {response.status_code}")
            st.write("Response:", response.json())
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Function to prepare product data for Shopify
def prepare_product_data(item_name, description, price, sku):
    """
    Prepares the product data in the format required by Shopify.
    
    Parameters:
        item_name (str): Name of the item.
        description (str): Description of the item.
        price (str or float): Price of the item.
        sku (str): SKU of the item.
    
    Returns:
        dict: Structured product data for Shopify API.
    """
    product_data = {
        "product": {
            "title": item_name,
            "body_html": description,
            "vendor": "Your Vendor",  # You can make this dynamic if needed
            "product_type": "Your Product Type",  # You can make this dynamic if needed
            "variants": [
                {
                    "price": price,
                    "sku": sku
                }
            ]
        }
    }
    return product_data

# Function to post product to Shopify
def post_product_to_shopify(product_data):
    """
    Posts a new product to the Shopify store.
    
    Parameters:
        product_data (dict): The product data structured for Shopify API.
    
    Returns:
        dict or None: Response from Shopify API if successful, None otherwise.
    """
    try:
        # Build the products URL
        products_url = f"https://{st.secrets['shopify_store']}.myshopify.com/admin/api/2023-01/products.json"
        
        # Get headers using admin API key
        headers = get_shopify_headers(use_admin_key=True)
        
        # Make a POST request to Shopify API
        response = requests.post(products_url, json=product_data, headers=headers)
        
        # Check response status
        if response.status_code == 201:
            st.success("Product posted successfully to Shopify!")
            return response.json()
        else:
            st.error(f"Failed to post product to Shopify. Status Code: {response.status_code}")
            st.write("Response:", response.json())
            return None
    except Exception as e:
        st.error(f"An error occurred while posting the product: {str(e)}")
        return None
