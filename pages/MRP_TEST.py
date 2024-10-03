# pages/mrp_dashboard.py

import streamlit as st
import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
from utils.restlet import fetch_restlet_data  # If this import causes issues, we will place the logic here.

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page title
st.title("MRP Dashboard")

# Function to fetch and cache raw data using a saved search ID
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    try:
        # Fetch raw data from the RESTlet endpoint
        data = fetch_restlet_data(saved_search_id)
        logger.info(f"Fetched {len(data)} rows for saved search ID: {saved_search_id}")
        st.write(f"Fetched {len(data)} rows for saved search ID: {saved_search_id}")  # Display fetched data length in UI for verification
        return data
    except Exception as e:
        logger.error(f"Failed to fetch raw data for {saved_search_id}: {e}")
        st.write(f"Failed to fetch raw data for {saved_search_id}: {e}")  # Show error message in UI
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to fetch and cache SuiteQL data
@st.cache_data(ttl=900)
def fetch_paginated_suiteql_data(query, base_url, secrets):
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
            response = requests.post(next_url, auth=auth, json=payload, headers={"Content-Type": "application/json", "Prefer": "transient"})
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])
            all_data.extend(items)

            # Check for next page link
            next_url = next((link['href'] for link in data.get("links", []) if link['rel'] == 'next'), None)

        logger.info(f"Fetched {len(all_data)} rows from SuiteQL.")
        st.write(f"Fetched {len(all_data)} rows from SuiteQL.")  # Display fetched data length in UI
        return pd.DataFrame(all_data)

    except Exception as e:
        logger.error(f"Failed to fetch SuiteQL data: {e}")
        st.write(f"Failed to fetch SuiteQL data: {e}")  # Show error message in UI
        return pd.DataFrame()  # Return an empty DataFrame on error

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

        # Fetch data
        logger.info("Fetching inventory data from SuiteQL...")
        inventory_df = fetch_paginated_suiteql_data(suiteql_query, base_url, secrets)
        st.write("Inventory DataFrame (Preview):", inventory_df.head())  # Display preview of inventory_df

        logger.info("Fetching sales data...")
        sales_df = fetch_raw_data("customsearch5141")
        st.write("Sales DataFrame (Preview):", sales_df.head())  # Display preview of sales_df

        logger.info("Fetching purchase data...")
        purchase_df = fetch_raw_data("customsearch5142")
        st.write("Purchase DataFrame (Preview):", purchase_df.head())  # Display preview of purchase_df

        # Check if all data frames are valid
        if inventory_df.empty:
            logger.warning("Inventory DataFrame is empty.")
            st.warning("Inventory DataFrame is empty.")
        if sales_df.empty:
            logger.warning("Sales DataFrame is empty.")
            st.warning("Sales DataFrame is empty.")
        if purchase_df.empty:
            logger.warning("Purchase DataFrame is empty.")
            st.warning("Purchase DataFrame is empty.")

        # Convert column names to lowercase for consistency
        inventory_df.columns = inventory_df.columns.str.lower()
        sales_df.columns = sales_df.columns.str.lower()
        purchase_df.columns = purchase_df.columns.str.lower()

        # Merge dataframes into a master dataframe
        logger.info("Merging dataframes into master dataframe...")
        master_df = inventory_df.merge(sales_df, on='item', how='outer').merge(purchase_df, on='item', how='outer')
        st.write("Master DataFrame (Preview):", master_df.head())  # Display preview of master_df

        logger.info(f"Master DataFrame created with {len(master_df)} rows.")
        return master_df

    except Exception as e:
        logger.error(f"Error creating master dataframe: {e}")
        st.write(f"Error creating master dataframe: {e}")  # Show error message in UI
        return pd.DataFrame()  # Return empty DataFrame on error

# Fetch the master dataframe with caching
@st.cache_data(ttl=900)
def get_master_dataframe():
    try:
        # Call the function to create the master DataFrame
        master_df = create_master_dataframe(st.secrets)
        return master_df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Fetch the master dataframe
master_df = get_master_dataframe()

# Check if the master_df is empty before proceeding
if master_df.empty:
    st.warning("No data available to display. Please check the data source or API configurations.")
else:
    st.success("Data loaded successfully.")
    # Display first few rows for verification
    st.write("Preview of the master data:")
    st.write(master_df.head())

    # Multiselect for item type and vendor
    item_type_options = sorted(master_df['item type'].dropna().unique())
    selected_item_types = st.multiselect('Select Item Type', options=item_type_options)

    vendor_options = sorted(pd.concat([master_df['vendor'], master_df['vendor']]).dropna().unique())
    selected_vendors = st.multiselect('Select Vendor', options=vendor_options)

    # Filter the data based on selections
    filtered_df = master_df[
        (master_df['item type'].isin(selected_item_types) if selected_item_types else True) &
        (master_df['vendor'].isin(selected_vendors) if selected_vendors else True)
    ]

    # Display the filtered DataFrame
    st.dataframe(filtered_df)

    # Download button for the filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(label="Download Filtered Data as CSV", data=csv, file_name='filtered_inventory_data.csv', mime='text/csv')
