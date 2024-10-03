# utils/mrp_master_df.py

import streamlit as st
import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
from utils.restlet import fetch_restlet_data

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to fetch raw data using a saved search ID with caching
@st.cache_data(ttl=900)  # Use st.cache_data for caching the raw data fetching
def fetch_raw_data(saved_search_id):
    logger.info(f"Fetching raw data for saved search ID: {saved_search_id}")
    try:
        data = fetch_restlet_data(saved_search_id)
        if data is None or data.empty:
            logger.warning(f"No data returned for saved search ID: {saved_search_id}")
            return pd.DataFrame()  # Return an empty DataFrame if no data is found
        return data
    except Exception as e:
        logger.error(f"Error fetching raw data for {saved_search_id}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on exception

# Function to fetch paginated SuiteQL data with caching
@st.cache_data(ttl=900)  # Use st.cache_data for caching the SuiteQL data fetching
def fetch_paginated_suiteql_data(query, base_url, secrets):
    logger.info(f"Fetching SuiteQL data with query: {query}")
    try:
        auth = OAuth1(
            secrets["consumer_key"],
            secrets["consumer_secret"],
            secrets["token_key"],
            secrets["token_secret"],
            realm=secrets["realm"],
            signature_method='HMAC-SHA256'
        )
        
        all_data = []
        next_url = base_url
        payload = {"q": query}

        while next_url:
            try:
                response = requests.post(next_url, auth=auth, json=payload, headers={"Content-Type": "application/json", "Prefer": "transient"})
                response.raise_for_status()

                data = response.json()
                items = data.get("items", [])
                all_data.extend(items)

                # Check for next page link
                next_url = next((link['href'] for link in data.get("links", []) if link['rel'] == 'next'), None)
            except Exception as e:
                logger.error(f"Error fetching SuiteQL data: {e}")
                break

        if not all_data:
            logger.warning(f"No data returned from SuiteQL query: {query}")
            return pd.DataFrame()  # Return empty DataFrame if no data is fetched

        return pd.DataFrame(all_data)
    except Exception as e:
        logger.error(f"Failed to fetch SuiteQL data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Function to create the master DataFrame
def create_master_dataframe(secrets):
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
        base_url = f"https://{secrets['realm']}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"

        # Fetch data using the appropriate functions
        inventory_df = fetch_paginated_suiteql_data(suiteql_query, base_url, secrets)
        sales_df = fetch_raw_data("customsearch5141")
        purchase_df = fetch_raw_data("customsearch5142")

        # Check if dataframes are valid
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
        master_df = inventory_df.merge(sales_df, on='item', how='outer').merge(purchase_df, on='item', how='outer')

        return master_df

    except Exception as e:
        logger.error(f"Error creating master dataframe: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error
