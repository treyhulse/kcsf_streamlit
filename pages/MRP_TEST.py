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
inventory_df = fetch_paginated_suiteql_data(suiteql_query, base_url)
sales_df = fetch_raw_data("customsearch5141")

# Display column names for debugging
st.write("Inventory DF Columns: ", inventory_df.columns.tolist())
st.write("Sales DF Columns: ", sales_df.columns.tolist())

# Ensure 'item' column for merging is consistent
inventory_df.columns = inventory_df.columns.str.lower()
sales_df.columns = sales_df.columns.str.lower()

# Merge dataframes on 'item'
if 'item' in inventory_df.columns and 'item' in sales_df.columns:
    master_df = inventory_df.merge(sales_df, on='item', how='outer')
else:
    st.error("Item column missing in one of the dataframes")
    master_df = pd.DataFrame()

# Multiselect for item type
item_type_options = master_df['item type'].unique() if 'item type' in master_df.columns else []
selected_item_types = st.multiselect('Select Item Type', options=item_type_options)

# Multiselect for vendor
vendor_options = master_df['vendor'].unique() if 'vendor' in master_df.columns else []
selected_vendors = st.multiselect('Select Vendor', options=vendor_options)

# Apply filters to dataframe
filtered_df = master_df[(master_df['item type'].isin(selected_item_types) if selected_item_types else True) &
                        (master_df['vendor'].isin(selected_vendors) if selected_vendors else True)]

# Display filtered DataFrame
st.dataframe(filtered_df)

# Download button for the filtered data
csv = filtered_df.to_csv(index=False)
st.download_button(label="Download Filtered Data as CSV", data=csv, file_name='filtered_inventory_data.csv', mime='text/csv')