import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Supply Chain Data",
    page_icon="📊",
    layout="wide",
)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Order Management'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
from utils.data_functions import process_netsuite_data_json

# Set up sales rep mapping (if needed for the 'salesrep' column)
sales_rep_mapping = {
    # Add mappings if necessary (e.g., '1': 'John Doe')
}

# Fetching estimates
estimate_url = f"{st.secrets['url_restlet']}?savedSearchId=customsearch5127"
estimate_data = process_netsuite_data_json(estimate_url, sales_rep_mapping)

# Fetching sales orders
sales_order_url = f"{st.secrets['url_restlet']}?savedSearchId=customsearch5122"
sales_order_data = process_netsuite_data_json(sales_order_url, sales_rep_mapping)


# Create tabs for Estimates and Sales Orders
tab1, tab2 = st.tabs(["Estimates", "Sales Orders"])

# Tab for Estimates
with tab1:
    st.header("Estimate Management")
    estimate_data = process_netsuite_data_json(estimate_url, sales_rep_mapping)
    if not estimate_data.empty:
        st.dataframe(estimate_data)
    else:
        st.write("No data available for Estimates.")

# Tab for Sales Orders
with tab2:
    st.header("Sales Order Management")
    sales_order_data = process_netsuite_data_json(sales_order_url, sales_rep_mapping)
    if not sales_order_data.empty:
        st.dataframe(sales_order_data)
    else:
        st.write("No data available for Sales Orders.")
