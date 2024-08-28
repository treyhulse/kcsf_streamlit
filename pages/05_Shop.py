import streamlit as st
import pandas as pd
from utils.data_functions import process_netsuite_data_json
from requests.exceptions import RequestException
from datetime import datetime, timedelta
import logging

# Set page config
st.set_page_config(page_title="Sales Orders", page_icon="📋", layout="wide")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Title
st.title("Active Work Orders")

# Sales Rep mapping
sales_rep_mapping = {
    7: "Shelley Gummig",
    61802: "Kaitlyn Surry",
    4125270: "Becky Dean",
    4125868: "Roger Dixon",
    4131659: "Lori McKiney",
    47556: "Raymond Brown",
    4169685: "Shellie Pritchett",
    4123869: "Katelyn Kennedy",
    47708: "Phil Vaughan",
    4169200: "Dave Knudtson",
    4168032: "Trey Hulse",
    4152972: "Gary Bargen",
    4159935: "Derrick Lewis",
    66736: "Unspecified",
    67473: 'Jon Joslin',
}

@st.cache_data
def fetch_data(url, mapping, retries=3, delay=5):
    """Fetch data from the NetSuite RESTlet API."""
    attempt = 0
    while attempt < retries:
        try:
            df_sales = process_netsuite_data_json(url, mapping)
            if df_sales.empty:
                st.warning("No data returned from the API. Please check your API and data source.")
                return pd.DataFrame()
            df_sales['trandate'] = pd.to_datetime(df_sales['trandate'])
            
            # Apply the sales rep mapping
            df_sales['salesrep'] = pd.to_numeric(df_sales['salesrep'], errors='coerce', downcast='integer')
            df_sales['salesrep'] = df_sales['salesrep'].map(mapping).fillna(df_sales['salesrep'])

            return df_sales
        except RequestException as e:
            attempt += 1
            st.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    st.error(f"Failed to fetch data after {retries} attempts.")
    return pd.DataFrame()

# Fetch data from API
logger.info("Fetching data from the API...")
df_sales = fetch_data(st.secrets["url_sales"], sales_rep_mapping)
if df_sales.empty:
    st.warning("No data fetched. Please check the API or data source.")
    st.stop()

logger.info("Data fetched successfully")

# Filter to include only fully billed orders
df_sales = df_sales[df_sales['statusref'] == 'fullyBilled']

# Ensure 'amount' is numeric
df_sales['amount'] = pd.to_numeric(df_sales['amount'], errors='coerce')

# Create job cards for each sales order
st.subheader("Active Work Orders")

# Determine max amount for progress calculation
max_amount = df_sales['amount'].max()

for index, row in df_sales.iterrows():
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])

        with col1:
            st.write(f"**Order ID:** {row['tranid']}")
        with col2:
            st.write(f"**Order Date:** {row['trandate'].date()}")
        with col3:
            st.write(f"**Customer:** {row['entity']}")
        with col4:
            st.write(f"**Amount:** ${row['amount']:,.2f}")
        with col5:
            st.write(f"**Sales Rep:** {row['salesrep']}")

        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 3])

        with col1:
            progress = row['amount'] / max_amount if max_amount else 0
            st.progress(progress)

        with col4:
            st.button(f"New Action", key=f"new_action_{row['tranid']}")

        with col5:
            if st.button(f"Change Status of {row['tranid']}", key=row['tranid']):
                st.write(f"Order {row['tranid']} status changed!")
                # Logic to change the status of the order would go here
                # This would typically involve making a call to NetSuite API to update the status

        st.write("---")

logger.info("Job cards with progress bars, new action buttons, and status change buttons displayed successfully")
