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
            return pd.DataFrame()  # Return an empty DataFrame on error

    return pd.DataFrame(all_data)

# Define the query and base URL
suiteql_query = """
SELECT
    invbal.item AS "item",
    item.displayname AS "display name",
    invbal.quantityonhand AS "quantity on hand",
    invbal.quantityavailable AS "quantity available",
    itype.description AS "item type",
    vend.companyname AS "vendor"
FROM
    inventorybalance invbal
JOIN
    item ON invbal.item = item.id
LEFT JOIN
    itemtype itype ON item.itemtype = itype.id
LEFT JOIN
    vendor vend ON item.preferredvendor = vend.id
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

# Check if dataframes are empty and convert column names to lowercase
for df in [inventory_df, sales_df, purchase_df]:
    if not df.empty:
        df.columns = df.columns.str.lower()
    else:
        st.error("Failed to load data for one or more dataframes. Please check the logs and data sources.")

# Joining dataframes on 'item'
if not inventory_df.empty and not sales_df.empty and not purchase_df.empty:
    master_df = inventory_df.merge(sales_df, on='item', how='outer').merge(purchase_df, on='item', how='outer')
    # Multiselect for filtering by 'item type'
    selected_item_types = st.multiselect('Select Item Type', options=master_df['item type'].unique())
    filtered_df = master_df[master_df['item type'].isin(selected_item_types)] if selected_item_types else master_df

    # Multiselect for filtering by 'vendor'
    selected_vendors = st.multiselect('Select Vendor', options=filtered_df['vendor'].unique())
    filtered_df = filtered_df[filtered_df['vendor'].isin(selected_vendors)] if selected_vendors else filtered_df

    # Displaying the filtered DataFrame
    st.dataframe(filtered_df)

    # Download button for the filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(label="Download Filtered Data as CSV", data=csv, file_name='filtered_inventory_data.csv', mime='text/csv')
else:
    st.error("Unable to merge dataframes as one or more are empty.")
