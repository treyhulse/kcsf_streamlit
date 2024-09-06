import requests
import streamlit as st


# Function to get the Shopify connection headers
def get_shopify_headers(use_admin_key=False):
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
    try:
        shop_url = f"https://{st.secrets['shopify_store']}.myshopify.com/admin/api/2023-01/shop.json"
        headers = get_shopify_headers(use_admin_key=True)
        response = requests.get(shop_url, headers=headers)
        if response.status_code == 200:
            st.success("Successfully connected to Shopify store!")
            return response.json()
        else:
            st.error(f"Failed to connect to Shopify. Status Code: {response.status_code}")
            st.write("Response:", response.json())
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Function to prepare product data for Shopify
def prepare_product_data(item_name, description, price, sku):
    product_data = {
        "product": {
            "title": item_name,
            "body_html": description,
            "vendor": "Your Vendor",
            "product_type": "Your Product Type",
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
    try:
        products_url = f"https://{st.secrets['shopify_store']}.myshopify.com/admin/api/2023-01/products.json"
        headers = get_shopify_headers(use_admin_key=True)
        response = requests.post(products_url, json=product_data, headers=headers)
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

# Function to retrieve synced products from Shopify
def get_synced_products_from_shopify():
    try:
        products_url = f"https://{st.secrets['shopify_store']}.myshopify.com/admin/api/2023-01/products.json"
        headers = get_shopify_headers(use_admin_key=True)
        response = requests.get(products_url, headers=headers)
        if response.status_code == 200:
            products = response.json().get('products', [])
            st.success(f"Retrieved {len(products)} products from Shopify.")
            return products
        else:
            st.error(f"Failed to retrieve products from Shopify. Status Code: {response.status_code}")
            st.write("Response:", response.json())
            return None
    except Exception as e:
        st.error(f"An error occurred while fetching products from Shopify: {str(e)}")
        return None
