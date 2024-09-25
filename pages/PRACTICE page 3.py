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

# Tab structure for switching between different views
tab1, tab2, tab3 = st.tabs(["Inventory Data", "Sales/Purchase Order Lines", "Supply and Demand Visibility"])

# First tab (Inventory Data)
with tab1:
    # Inventory fetching logic
    suiteql_query = """
    SELECT
        invbal.item AS "Item ID",
        item.displayname AS "Item",
        invbal.binnumber AS "Bin Number",
        invbal.location AS "Warehouse",
        invbal.inventorynumber AS "Inventory Number",
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
    
    # Fetch the inventory data
    inventory_df = fetch_paginated_suiteql_data(suiteql_query, base_url)
    
    if not inventory_df.empty:
        st.success(f"Successfully fetched {len(inventory_df)} records.")
        st.dataframe(inventory_df)
    else:
        st.error("No data available or an error occurred during data fetching.")

# Second tab (Sales and Purchase Order Lines)
with tab2:
    customsearch5141_data = fetch_raw_data("customsearch5141")
    customsearch5142_data = fetch_raw_data("customsearch5142")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Sales Order Lines")
        if not customsearch5141_data.empty:
            st.dataframe(customsearch5141_data)
        else:
            st.write("No data available for customsearch5141.")

    with col2:
        st.write("Purchase Order Lines")
        if not customsearch5142_data.empty:
            st.dataframe(customsearch5142_data)
        else:
            st.write("No data available for Purchase Order Lines.")

# Third tab (Supply and Demand Visibility)
with tab3:
    # Combine the Inventory, Sales Orders, and Purchase Orders DataFrames
    inventory_sales_df = pd.merge(inventory_df, customsearch5141_data, left_on='item id', right_on='Item', how='outer')
    supply_demand_df = pd.merge(inventory_sales_df, customsearch5142_data, left_on='item id', right_on='Item', how='outer')

    # Simplify the resulting DataFrame and add Net Inventory
    supply_demand_df = supply_demand_df[['item', 'bin number', 'warehouse', 'quantity available', 'quantity on hand',
                                         'Ordered_x', 'Committed', 'Fulfilled_x', 'Back Ordered',
                                         'Ordered_y', 'Fulfilled_y', 'Not Received']]

    # Rename columns for clarity
    supply_demand_df.columns = ['Item', 'Bin Number', 'Warehouse', 'Available Quantity', 'On Hand Quantity',
                                'Sales Ordered', 'Sales Committed', 'Sales Fulfilled', 'Sales Back Ordered',
                                'Purchase Ordered', 'Purchase Fulfilled', 'Purchase Not Received']

    # Convert the relevant columns to numeric types to avoid type errors
    numeric_cols = ['Available Quantity', 'On Hand Quantity', 'Sales Ordered', 'Sales Back Ordered', 'Purchase Ordered']
    supply_demand_df[numeric_cols] = supply_demand_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Fill NaN values with 0 for better visibility
    supply_demand_df.fillna(0, inplace=True)

    # Add Net Inventory column
    supply_demand_df['Net Inventory'] = (supply_demand_df['Available Quantity'] + supply_demand_df['Purchase Ordered']) - \
                                        (supply_demand_df['Sales Ordered'] + supply_demand_df['Sales Back Ordered'])

    # Display the DataFrame in Streamlit
    st.write("Supply and Demand Visibility with Net Inventory")
    st.dataframe(supply_demand_df)

    # Option to download the data as CSV
    csv = supply_demand_df.to_csv(index=False)
    st.download_button(label="Download data as CSV", data=csv, file_name='supply_demand_visibility.csv', mime='text/csv')
