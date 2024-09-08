# apis.py
import streamlit as st
import requests
from utils.connections import connect_to_netsuite, connect_to_shopify

# Fetch products from NetSuite marked for Shopify channel
def get_netsuite_products():
    netsuite_url, headers = connect_to_netsuite()
    response = requests.get(f"{netsuite_url}/products", headers=headers)  # Modify URL based on your endpoint
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        return []

# Fetch products from Shopify
def get_shopify_products():
    shopify_url, headers = connect_to_shopify(use_admin_key=True)
    response = requests.get(f"{shopify_url}products.json", headers=headers)
    if response.status_code == 200:
        return response.json().get('products', [])
    else:
        return []

# Post product to Shopify
def post_product_to_shopify(product_data):
    shopify_url, headers = connect_to_shopify(use_admin_key=True)
    response = requests.post(f"{shopify_url}products.json", json=product_data, headers=headers)
    return response.status_code, response.json()

# Update product on Shopify
def update_product_on_shopify(product_id, update_data):
    shopify_url, headers = connect_to_shopify(use_admin_key=True)
    response = requests.put(f"{shopify_url}products/{product_id}.json", json=update_data, headers=headers)
    return response.status_code, response.json()

# Fetch products from NetSuite with SKU checking
def sku_exists_on_netsuite(sku):
    netsuite_url, headers = connect_to_netsuite()
    response = requests.get(f"{netsuite_url}/products?sku={sku}", headers=headers)
    return response.status_code == 200 and response.json().get('results', [])

# Update inventory and price in Shopify
def update_inventory_and_price(product_id, inventory, price):
    update_data = {
        "product": {
            "variants": [
                {
                    "inventory_quantity": inventory,
                    "price": price
                }
            ]
        }
    }
    return update_product_on_shopify(product_id, update_data)

# Fetch products from NetSuite using RESTlet
def get_netsuite_products_via_restlet():
    netsuite_url = st.secrets['shopifyitemsurl']  # Update with the RESTlet URL
    headers = {
        "Authorization": f"OAuth oauth_consumer_key={st.secrets['consumer_key']}, "
                         f"oauth_token={st.secrets['token_key']}, "
                         f"oauth_signature_method=HMAC-SHA256, "
                         f"oauth_signature={st.secrets['consumer_secret']}&{st.secrets['token_secret']}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(netsuite_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch products from NetSuite. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching products from NetSuite: {str(e)}")
        return []