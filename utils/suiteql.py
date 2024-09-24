# utils.suiteql.py
import requests
from requests_oauthlib import OAuth1
import streamlit as st
import pandas as pd
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication setup for SuiteQL requests
def get_authentication():
    """
    Returns an OAuth1 object for authenticating SuiteQL requests.
    Credentials are stored in st.secrets.
    """
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

def fetch_suiteql_data(query, max_retries=3):
    """
    Fetches data from NetSuite's SuiteQL API.
    
    Args:
        query (str): The SuiteQL query string.
        max_retries (int): Maximum retry attempts in case of failure.
    
    Returns:
        pd.DataFrame: DataFrame containing the results of the query.
    """
    url = f"https://{st.secrets['realm']}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    auth = get_authentication()
    all_data = []

    payload = {"q": query}

    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching SuiteQL data with query: {query}")
            response = requests.post(url, auth=auth, json=payload, headers={"Content-Type": "application/json", "Prefer": "transient"})
            response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

            # Assuming the response is in JSON format
            data = response.json().get('items', [])

            if not data:
                logger.info("No data returned.")
                return pd.DataFrame(all_data) if all_data else pd.DataFrame()

            all_data.extend(data)
            logger.info(f"Successfully fetched {len(data)} records.")
            return pd.DataFrame(all_data)

        except Exception as e:
            logger.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                st.error(f"Failed to fetch data after {max_retries} attempts.")
                return pd.DataFrame(all_data) if all_data else pd.DataFrame()
            time.sleep(2 ** attempt)  # Exponential backoff


def fetch_netsuite_inventory():
    """
    Fetches the inventory balance data from NetSuite using SuiteQL.
    
    Returns:
        pd.DataFrame: DataFrame containing the inventory balance results.
    """
    suiteql_inventory_query = """
    SELECT
        invbal.item AS "Item ID",
        item.displayname AS "Item",
        invbal.binnumber AS "Bin Number",
        invbal.location AS "Warehouse",
        invbal.inventorynumber AS "Inventory Number",
        invbal.quantityonhand AS "Quantity On Hand",  -- Correct field name for "On Hand"
        invbal.quantityavailable AS "Quantity Available"  -- Correct field name for "Available"
    FROM
        inventorybalance invbal
    JOIN
        item ON invbal.item = item.id
    WHERE
        item.isinactive = 'F'  -- Only active items
    ORDER BY
        item.displayname ASC;
    """
    return fetch_suiteql_data(suiteql_inventory_query)
