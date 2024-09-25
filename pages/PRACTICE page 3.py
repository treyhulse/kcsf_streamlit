import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import pandas as pd
import plotly.express as px

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
from utils.restlet import fetch_restlet_data
from utils.suiteql import fetch_paginated_suiteql_data, base_url

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page title
st.title("MRP Dashboard")

# Cache the raw data fetching process (TTL: 900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    return fetch_restlet_data(saved_search_id)

# SuiteQL query function to fetch inventory data
@st.cache_data(ttl=900)
def fetch_inventory_data(suiteql_query, base_url):
    return fetch_paginated_suiteql_data(suiteql_query, base_url)

# Define the SuiteQL query for the inventory data
suiteql_query = """
SELECT
    invbal.item AS "item id",
    item.displayname AS "Item",
    invbal.location AS "Warehouse",
    invbal.quantityonhand AS "Quantity On Hand",
    invbal.quantityavailable AS "Quantity Available"
FROM
    inventorybalance invbal
JOIN
    item ON invbal.item = item.id
WHERE
    item.isinactive = 'F'
ORDER BY
    item.displayname ASC;
"""

# Base URL for SuiteQL API
base_url = f"https://{st.secrets['realm']}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"

# Fetch the inventory data from SuiteQL query
inventory_df = fetch_inventory_data(suiteql_query, base_url)

# Fetch sales order and purchase order data using saved search IDs
sales_orders_df = fetch_raw_data("customsearch5141")  # Example saved search for sales orders
purchase_orders_df = fetch_raw_data("customsearch5142")  # Example saved search for purchase orders

# Rename 'item id' in the inventory table to match 'Item' in sales/purchase orders
inventory_df.rename(columns={'item id': 'Item'}, inplace=True)

# Merge the data on 'Item' and 'Warehouse'
merged_df = pd.merge(inventory_df, sales_orders_df, on=['Item', 'Warehouse'], how='outer')
merged_df = pd.merge(merged_df, purchase_orders_df, on=['Item', 'Warehouse'], how='outer')

# Group by 'Item' and 'Warehouse' and sum relevant columns
supply_demand_df = merged_df.groupby(['Item', 'Warehouse'], as_index=False).agg({
    'Quantity Available': 'sum',
    'Quantity On Hand': 'sum',
    'Ordered_x': 'sum',  # Sales Ordered
    'Committed': 'sum',
    'Fulfilled_x': 'sum',  # Sales Fulfilled
    'Back Ordered': 'sum',
    'Ordered_y': 'sum',  # Purchase Ordered
    'Fulfilled_y': 'sum',  # Purchase Fulfilled
    'Not Received': 'sum'
})

# Rename columns for clarity
supply_demand_df.columns = ['Item', 'Warehouse', 'Available Quantity', 'On Hand Quantity',
                            'Sales Ordered', 'Sales Committed', 'Sales Fulfilled',
                            'Sales Back Ordered', 'Purchase Ordered', 'Purchase Fulfilled',
                            'Purchase Not Received']

# Fill NaN values with 0
supply_demand_df.fillna(0, inplace=True)

# Add Net Inventory column
supply_demand_df['Net Inventory'] = (supply_demand_df['Available Quantity'] + supply_demand_df['Purchase Ordered']) - \
                                    (supply_demand_df['Sales Ordered'] + supply_demand_df['Sales Back Ordered'])

# Add a filter for Warehouse
warehouse_options = supply_demand_df['Warehouse'].unique()
selected_warehouse = st.selectbox("Select Warehouse", options=warehouse_options)

# Filter by the selected warehouse
filtered_df = supply_demand_df[supply_demand_df['Warehouse'] == selected_warehouse]

# Display the filtered DataFrame
st.write(f"Supply and Demand Visibility for Warehouse {selected_warehouse}")
st.dataframe(filtered_df)

# Option to download the data as CSV
csv = filtered_df.to_csv(index=False)
st.download_button(label="Download data as CSV", data=csv, file_name='supply_demand_visibility.csv', mime='text/csv')
