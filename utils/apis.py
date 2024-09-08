# utils/apis.py
import requests
import streamlit as st
import logging
from utils.connections import connect_to_netsuite, connect_to_shopify

# Setup logging
logging.basicConfig(level=logging.INFO)

# Fetch products from NetSuite using RESTlet
def get_netsuite_products_via_restlet():
    try:
        netsuite_url = st.secrets['shopifyitems_url']  # Updated with the new key name
        headers = {
            "Authorization": f"OAuth oauth_consumer_key={st.secrets['consumer_key']}, "
                             f"oauth_token={st.secrets['token_key']}, "
                             f"oauth_signature_method=HMAC-SHA256, "
                             f"oauth_signature={st.secrets['consumer_secret']}&{st.secrets['token_secret']}",
            "Content-Type": "application/json"
        }

        logging.info(f"Fetching products from NetSuite RESTlet URL: {netsuite_url}")
        response = requests.get(netsuite_url, headers=headers)
        if response.status_code == 200:
            logging.info("NetSuite products retrieved successfully.")
            return response.json()
        else:
            logging.error(f"Failed to fetch products from NetSuite. Status code: {response.status_code}")
            st.error(f"Failed to fetch products from NetSuite. Status code: {response.status_code}")
            return []
    except KeyError as e:
        logging.error(f"Missing secret: {e}")
        st.error(f"Missing secret: {e}")
        return []
    except Exception as e:
        logging.error(f"An error occurred while fetching products from NetSuite: {str(e)}")
        st.error(f"An error occurred while fetching products from NetSuite: {str(e)}")
        return []

# Fetch products from Shopify
def get_shopify_products():
    try:
        shopify_url, headers = connect_to_shopify(use_admin_key=True)
        response = requests.get(f"{shopify_url}products.json", headers=headers)
        if response.status_code == 200:
            logging.info("Shopify products retrieved successfully.")
            return response.json().get('products', [])
        else:
            logging.error(f"Failed to fetch products from Shopify. Status code: {response.status_code}")
            st.error(f"Failed to fetch products from Shopify. Status code: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"An error occurred while fetching products from Shopify: {str(e)}")
        st.error(f"An error occurred while fetching products from Shopify: {str(e)}")
        return []

# Post product to Shopify
def post_product_to_shopify(product_data):
    try:
        shopify_url, headers = connect_to_shopify(use_admin_key=True)
        response = requests.post(f"{shopify_url}products.json", json=product_data, headers=headers)
        if response.status_code == 201:
            logging.info("Product posted successfully to Shopify.")
            return response.status_code, response.json()
        else:
            logging.error(f"Failed to post product to Shopify. Status code: {response.status_code}")
            st.error(f"Failed to post product to Shopify. Status code: {response.status_code}")
            return response.status_code, response.json()
    except Exception as e:
        logging.error(f"An error occurred while posting the product to Shopify: {str(e)}")
        st.error(f"An error occurred while posting the product to Shopify: {str(e)}")
        return None, None

# Update product on Shopify
def update_product_on_shopify(product_id, update_data):
    try:
        shopify_url, headers = connect_to_shopify(use_admin_key=True)
        response = requests.put(f"{shopify_url}products/{product_id}.json", json=update_data, headers=headers)
        if response.status_code == 200:
            logging.info(f"Product {product_id} updated successfully on Shopify.")
            return response.status_code, response.json()
        else:
            logging.error(f"Failed to update product {product_id} on Shopify. Status code: {response.status_code}")
            st.error(f"Failed to update product {product_id} on Shopify. Status code: {response.status_code}")
            return response.status_code, response.json()
    except Exception as e:
        logging.error(f"An error occurred while updating the product on Shopify: {str(e)}")
        st.error(f"An error occurred while updating the product on Shopify: {str(e)}")
        return None, None
