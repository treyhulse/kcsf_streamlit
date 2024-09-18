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

from utils.data_functions import fetch_all_data_json

# External RESTlet URL (without pagination, since that was causing issues)
restlet_url_base = "https://3429264.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=1718&deploy=1"

# Create tabs for Estimates and Sales Orders
tab1, tab2 = st.tabs(["Estimates", "Sales Orders"])

# Tab for Estimates
with tab1:
    st.header("Estimate Management")
    
    # Build the full URL by appending the saved search ID
    estimate_url = f"{restlet_url_base}&savedSearchId=customsearch5127"
    
    # Fetch and display Estimate data
    estimate_data = fetch_all_data_json(estimate_url)
    if not estimate_data.empty:
        st.dataframe(estimate_data)
    else:
        st.write("No data available for Estimates.")

# Tab for Sales Orders
with tab2:
    st.header("Sales Order Management")
    
    # Build the full URL by appending the saved search ID
    sales_order_url = f"{restlet_url_base}&savedSearchId=customsearch5122"
    
    # Fetch and display Sales Order data
    sales_order_data = fetch_all_data_json(sales_order_url)
    if not sales_order_data.empty:
        st.dataframe(sales_order_data)
    else:
        st.write("No data available for Sales Orders.")
