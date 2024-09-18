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
from utils.restlet import fetch_restlet_data


# Create tabs for Estimates and Sales Orders
tab1, tab2 = st.tabs(["Estimates", "Sales Orders"])

# Tab for Estimates
with tab1:
    st.header("Estimate Management")
    
    # Fetch and display Estimate data
    estimate_data = fetch_restlet_data("customsearch5127")
    
    if not estimate_data.empty:
        # Display the DataFrame
        st.dataframe(estimate_data)
    else:
        st.write("No data available for Estimates.")

# Tab for Sales Orders
with tab2:
    st.header("Sales Order Management")
    
    # Fetch and display Sales Order data
    sales_order_data = fetch_restlet_data("customsearch5122")
    
    if not sales_order_data.empty:
        # Display the DataFrame
        st.dataframe(sales_order_data)
    else:
        st.write("No data available for Sales Orders.")
