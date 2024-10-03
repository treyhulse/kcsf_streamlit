import streamlit as st
import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
from utils.restlet import fetch_restlet_data

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page title
st.title("MRP Dashboard")

# Function to fetch and cache data
@st.cache(ttl=900, allow_output_mutation=True)
def fetch_raw_data(saved_search_id):
    return fetch_restlet_data(saved_search_id)

# Function to fetch SuiteQL data
@st.cache(ttl=900, allow_output_mutation=True)
def fetch_paginated_suiteql_data(query, base_url):
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
        try:
            response = requests.post(next_url, auth=auth, json=payload, headers={"Content-Type": "application/json", "Prefer": "transient"})
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])
            all_data.extend(items)

            next_url = next((link['href'] for link in data.get("links", []) if link['rel'] == 'next'), None)
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            break

    return pd.DataFrame(all_data)

# SuiteQL query for inventory data
suiteql_query = """
SELECT
    invbal.item AS "item",
    item.displayname AS "display name",
    invbal.quantityonhand AS "quantity on hand",
    invbal.quantityavailable AS "quantity available"
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

# Fetch all data
inventory_df = fetch_paginated_suiteql_data(suiteql_query, base_url)
sales_df = fetch_raw_data("customsearch5141")
purchase_df = fetch_raw_data("customsearch5142")

# Convert column names to lowercase
inventory_df.columns = inventory_df.columns.str.lower()
sales_df.columns = sales_df.columns.str.lower()
purchase_df.columns = purchase_df.columns.str.lower()

# Joining dataframes on 'item'
master_df = inventory_df.merge(sales_df, on='item', how='outer').merge(purchase_df, on='item', how='outer')

# Handling duplicates and aggregating data
master_df = master_df.groupby('item').agg({
    'display name': 'first',  # Keeps the first non-null display name
    'quantity on hand': 'sum',
    'quantity available': 'sum'
}).reset_index()

# Tab structure for switching between different views
tab1, tab2 = st.tabs(["Inventory Data", "Sales/Purchase Order Lines"])

with tab1:
    # Displaying the master DataFrame
    st.write("Aggregated Inventory and Orders Data")
    st.dataframe(master_df)
    # Download button for the aggregated data
    csv = master_df.to_csv(index=False)
    st.download_button(label="Download Combined Data as CSV", data=csv, file_name='combined_inventory_data.csv', mime='text/csv')

with tab2:
    # Create two columns to display the individual saved search data side by side
    col1, col2 = st.columns(2)
    with col1:
        st.write("Sales Order Lines")
        if not sales_df.empty:
            st.dataframe(sales_df)
        else:
            st.write("No data available for customsearch5141.")
    with col2:
        st.write("Purchase Order Lines")
        if not purchase_df.empty:
            st.dataframe(purchase_df)
        else:
            st.write("No data available for Purchase Order Lines.")
