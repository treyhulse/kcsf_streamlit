import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

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
page_name = 'MRP'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

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

# Cache the raw data fetching process (TTL: 900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    return fetch_restlet_data(saved_search_id)

# Tab structure for switching between different views
tab1, tab2 = st.tabs(["Inventory Data", "Sales/Purchase Order Lines"])

# First tab (existing functionality for inventory data)
with tab1:

    # Authentication setup for SuiteQL requests
    def get_authentication():
        """
        Returns an OAuth1 object for authenticating SuiteQL requests.
        Credentials are stored in st.secrets.
        """
        return OAuth1(
            st.secrets["consumer_key"],
            st.secrets["consumer_secret"],
            st.secrets["token_key"],
            st.secrets["token_secret"],
            realm=st.secrets["realm"],
            signature_method='HMAC-SHA256'
        )

    # Function to fetch paginated SuiteQL data
    def fetch_paginated_suiteql_data(query, base_url):
        """
        Fetches paginated data from SuiteQL by following 'next' links.
        
        Args:
            query (str): SuiteQL query.
            base_url (str): Base URL for NetSuite's SuiteQL API.
        
        Returns:
            pd.DataFrame: A DataFrame containing all paginated results.
        """
        auth = get_authentication()
        all_data = []
        next_url = base_url
        payload = {"q": query}

        while next_url:
            try:
                response = requests.post(next_url, auth=auth, json=payload, headers={"Content-Type": "application/json", "Prefer": "transient"})
                response.raise_for_status()  # Raise error for bad responses

                data = response.json()
                items = data.get("items", [])

                if not items:
                    logger.info("No more data returned.")
                    break

                all_data.extend(items)
                logger.info(f"Fetched {len(items)} records. Total so far: {len(all_data)}")

                # Check if there's a next page
                links = data.get("links", [])
                next_link = next((link['href'] for link in links if link['rel'] == 'next'), None)
                next_url = next_link if next_link else None  # Continue to next page if available

            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                break

        return pd.DataFrame(all_data)

    # SuiteQL query
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

    # Base URL for SuiteQL API
    base_url = f"https://{st.secrets['realm']}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"

    # Fetch and display data
    st.write("Loading data from NetSuite...")

    # Fetch the paginated data
    inventory_df = fetch_paginated_suiteql_data(suiteql_query, base_url)

    if not inventory_df.empty:
        st.success(f"Successfully fetched {len(inventory_df)} records.")
        st.dataframe(inventory_df)  # Display the DataFrame in Streamlit

        # Option to download the data as CSV
        csv = inventory_df.to_csv(index=False)
        st.download_button(label="Download data as CSV", data=csv, file_name='inventory_data.csv', mime='text/csv')
    else:
        st.error("No data available or an error occurred during data fetching.")

# Second tab (two saved searches side by side)
with tab2:
    st.write("Rendering data from saved searches")

    # Fetch data for the two saved searches
    customsearch5141_data = fetch_raw_data("customsearch5141")
    customsearch5142_data = fetch_raw_data("customsearch5142")

    # Create two columns to display the data side by side
    col1, col2 = st.columns(2)

    # Left column: customsearch5141 data
    with col1:
        st.write("Sales Order Lines")
        if not customsearch5141_data.empty:
            st.dataframe(customsearch5141_data)
        else:
            st.write("No data available for customsearch5141.")

    # Right column: customsearch5142 data
    with col2:
        st.write("Purchase Order Lines")
        if not customsearch5142_data.empty:
            st.dataframe(customsearch5142_data)
        else:
            st.write("No data available for Purchase Order Lines.")
