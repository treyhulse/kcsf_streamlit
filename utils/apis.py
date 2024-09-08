# utils/apis.py
import requests
import pandas as pd
from io import StringIO
import logging
import streamlit as st
import time
from utils.connections import get_authentication, connect_to_netsuite, connect_to_shopify

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)

# Fetch all data from NetSuite RESTlet endpoint that returns CSV data
def fetch_all_data_csv(url, max_retries=3):
    """Fetch all data from a NetSuite RESTlet endpoint that returns CSV data."""
    all_data = []
    page = 1
    auth = get_authentication()

    while True:
        for attempt in range(max_retries):
            try:
                logging.info(f"Fetching page {page} from {url}")
                response = requests.get(f"{url}&page={page}", auth=auth)
                response.raise_for_status()

                # Assume the response is CSV
                df = pd.read_csv(StringIO(response.text))

                if df.empty:
                    logging.info("Received empty dataframe. Assuming end of data.")
                    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

                all_data.append(df)
                logging.info(f"Successfully fetched {len(df)} records from page {page}")

                if len(df) < 1000:  # Assuming 1000 is the max page size
                    logging.info("Received less than 1000 records. Assuming last page.")
                    return pd.concat(all_data, ignore_index=True)

                page += 1
                break  # Success, move to next page
            except Exception as e:
                logging.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    st.error(f"Failed to fetch data after {max_retries} attempts.")
                    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
                time.sleep(2 ** attempt)  # Exponential backoff

# Fetch all data from NetSuite RESTlet endpoint that returns JSON data
def fetch_all_data_json(url, max_retries=3):
    """Fetch all data from a NetSuite RESTlet endpoint that returns JSON data."""
    all_data = []
    page = 1
    auth = get_authentication()

    while True:
        for attempt in range(max_retries):
            try:
                logging.info(f"Fetching page {page} from {url}")
                response = requests.get(f"{url}&page={page}", auth=auth)
                response.raise_for_status()

                # Assuming the response is in JSON format
                data = response.json()

                if not data or len(data) == 0:
                    logging.info("Received empty data. Assuming end of data.")
                    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

                all_data.extend(data)
                logging.info(f"Successfully fetched {len(data)} records from page {page}")

                if len(data) < 1000:  # Assuming 1000 is the max page size
                    logging.info("Received less than 1000 records. Assuming last page.")
                    return pd.DataFrame(all_data)

                page += 1
                break  # Success, move to next page
            except Exception as e:
                logging.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    st.error(f"Failed to fetch data after {max_retries} attempts.")
                    return pd.DataFrame(all_data) if all_data else pd.DataFrame()
                time.sleep(2 ** attempt)  # Exponential backoff

# Helper function to replace IDs with display values using a mapping dictionary
def replace_ids_with_display_values(df, mapping_dict):
    """Replace internal IDs with their corresponding display values using a provided mapping."""
    if 'salesrep' in df.columns:
        df['salesrep'] = df['salesrep'].replace(mapping_dict)
    return df

# Fetch products from NetSuite using RESTlet
def get_netsuite_products_via_restlet():
    try:
        netsuite_url = st.secrets['url']  # Using the secret for RESTlet URL
        netsuite_base_url, headers = connect_to_netsuite()  # OAuth headers from connection

        if netsuite_url and headers:
            logging.info(f"Fetching products from NetSuite RESTlet: {netsuite_url}")
            
            # Make the request to NetSuite RESTlet
            response = requests.get(netsuite_url, headers=headers)
            
            # Check response status and handle errors
            if response.status_code == 200:
                logging.info("NetSuite products retrieved successfully.")
                return response.json()  # Return JSON data
            elif response.status_code == 401:
                logging.error("Unauthorized access. Check the OAuth headers or role permissions.")
                st.error(f"Failed to fetch products from NetSuite. Status code: 401 (Unauthorized)")
            else:
                logging.error(f"Failed to fetch products from NetSuite. Status code: {response.status_code}")
                st.error(f"Failed to fetch products from NetSuite. Status code: {response.status_code}")
                return []
        else:
            logging.error("NetSuite URL or OAuth headers missing.")
            st.error("NetSuite URL or OAuth headers missing.")
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

# Update inventory and price in Shopify
def update_inventory_and_price(product_id, inventory, price):
    try:
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
        status_code, response = update_product_on_shopify(product_id, update_data)
        if status_code == 200:
            logging.info(f"Inventory and price updated for product {product_id}.")
            return response
        else:
            logging.error(f"Failed to update inventory and price for product {product_id}.")
            return None
    except Exception as e:
        logging.error(f"An error occurred while updating inventory and price: {str(e)}")
        st.error(f"An error occurred while updating inventory and price: {str(e)}")
        return None
