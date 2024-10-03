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
purchase_df = fetch_raw_data("customsearch5142")

# Convert column names to lowercase
inventory_df.columns = inventory_df.columns.str.lower()
sales_df.columns = sales_df.columns.str.lower()
purchase_df.columns = purchase_df.columns.str.lower()

# Merge dataframes
master_df = inventory_df.merge(sales_df, on='item', how='outer').merge(purchase_df, on='item', how='outer')

# Function to handle 'All' selection
def handle_all_selection(options, default_text='All'):
    selected = st.multiselect("Select", options=[default_text] + options)
    return selected if default_text not in selected or len(selected) == 1 else options

# Multiselect for item type and vendor with 'All' handling
selected_item_types = handle_all_selection(sorted(master_df['item type'].dropna().unique()), 'All Item Types')
selected_vendors = handle_all_selection(sorted(pd.concat([sales_df['vendor'], purchase_df['vendor']]).dropna().unique()), 'All Vendors')

# Filter the data based on selections
filtered_df = master_df
if selected_item_types != ['All Item Types']:
    filtered_df = filtered_df[filtered_df['item type'].isin(selected_item_types)]
if selected_vendors != ['All Vendors']:
    filtered_df = filtered_df[filtered_df['vendor'].isin(selected_vendors)]

# Item search and metrics display
selected_item = st.selectbox('Search Item', options=filtered_df['item'].unique())
item_data = filtered_df[filtered_df['item'] == selected_item]

# Displaying metrics
metrics_cols = ['quantity on hand', 'quantity available', 'quantity incoming', 'quantity backordered']  # Ensure these are your column names
values = [item_data[col].sum() for col in metrics_cols]
col1, col2, col3, col4 = st.columns(4)
columns = [col1, col2, col3, col4]
for col, metric, value in zip(columns, metrics_cols, values):
    col.metric(metric.replace('_', ' ').title(), value)

# Split view for sales and purchase orders
sales_orders = item_data[item_data['order_type'] == 'sales']  # Adjust if 'order_type' is defined differently
purchase_orders = item_data[item_data['order_type'] == 'purchase']

col1, col2 = st.columns(2)
with col1:
    st.write("Sales Orders")
    st.dataframe(sales_orders[['item', 'order_id', 'quantity', 'date']])  # Adjust columns as per your data
with col2:
    st.write("Purchase Orders")
    st.dataframe(purchase_orders[['item', 'order_id', 'quantity', 'date']])

# Download button for the filtered data
csv = filtered_df.to_csv(index=False)
st.download_button("Download Filtered Data as CSV", data=csv, file_name='filtered_inventory_data.csv', mime='text/csv')
