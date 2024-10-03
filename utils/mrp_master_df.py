# utils/mrp_master_df.py

import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
import streamlit as st  # Import streamlit to access st.secrets globally

from utils.restlet import fetch_restlet_data

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to fetch and cache raw data using a saved search ID
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    try:
        # Fetch raw data from the RESTlet endpoint
        data = fetch_restlet_data(saved_search_id)
        logger.info(f"Fetched {len(data)} rows for saved search ID: {saved_search_id}")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch raw data for {saved_search_id}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to fetch and cache SuiteQL data
@st.cache_data(ttl=900)
def fetch_paginated_suiteql_data(query, base_url):
    try:
        # Use st.secrets directly for the OAuth1 setup
        auth = OAuth1(
            st.secrets["consumer_key"],
            st.secrets["consumer_secret"],
            st.secrets["token_key"],
            st.secrets["token_secret"],
            realm=st.secrets["realm"],
            signature_method='HMAC-SHA256'
        )

        all_data = []
        next_url = base_url
        payload = {"q": query}

        while next_url:
            response = requests.post(next_url, auth=auth, json=payload, headers={"Content-Type": "application/json", "Prefer": "transient"})
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])
            all_data.extend(items)

            # Check for next page link
            next_url = next((link['href'] for link in data.get("links", []) if link['rel'] == 'next'), None)

        logger.info(f"Fetched {len(all_data)} rows from SuiteQL.")
        return pd.DataFrame(all_data)

    except Exception as e:
        logger.error(f"Failed to fetch SuiteQL data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to create the master DataFrame
def create_master_dataframe():
    try:
        # SuiteQL query for inventory data including item type
        suiteql_query = """
        SELECT
            invbal.item AS "item",
            item.displayname AS "display name",
            invbal.quantityonhand AS "quantity on hand",
            invbal.quantityavailable AS "quantity available",
            item.itemtype AS "item type"
        FROM
            inventorybalance invbal
        JOIN
            item ON invbal.item = item.id
        WHERE
            item.isinactive = 'F'
        ORDER BY
            item.displayname ASC;
        """
        base_url = f"https://{st.secrets['realm']}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"

        # Fetch data
        logger.info("Fetching inventory data from SuiteQL...")
        inventory_df = fetch_paginated_suiteql_data(suiteql_query, base_url)

        logger.info("Fetching sales data...")
        sales_df = fetch_raw_data("customsearch5141")

        logger.info("Fetching purchase data...")
        purchase_df = fetch_raw_data("customsearch5142")

        # Check if all data frames are valid
        if inventory_df.empty:
            logger.warning("Inventory DataFrame is empty.")
        if sales_df.empty:
            logger.warning("Sales DataFrame is empty.")
        if purchase_df.empty:
            logger.warning("Purchase DataFrame is empty.")

        # Convert column names to lowercase for consistency
        inventory_df.columns = inventory_df.columns.str.lower()
        sales_df.columns = sales_df.columns.str.lower()
        purchase_df.columns = purchase_df.columns.str.lower()

        # Merge dataframes into a master dataframe
        logger.info("Merging dataframes into master dataframe...")
        master_df = inventory_df.merge(sales_df, on='item', how='outer').merge(purchase_df, on='item', how='outer')

        logger.info(f"Master DataFrame created with {len(master_df)} rows.")
        return master_df

    except Exception as e:
        logger.error(f"Error creating master dataframe: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error
