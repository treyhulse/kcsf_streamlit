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
import pandas as pd

# Function to calculate key metrics
def calculate_metrics(df, df_type):
    total_records = df.shape[0]
    outstanding_amount = df['Amount Remaining'].astype(float).sum()
    
    if df_type == "estimates":
        st.metric("Total Estimates Open", total_records)
        st.metric("$ Outstanding from Estimates", f"${outstanding_amount:,.2f}")
    elif df_type == "sales_orders":
        st.metric("Total Sales Orders Open", total_records)
        st.metric("$ Outstanding from Sales Orders", f"${outstanding_amount:,.2f}")

# Sidebar filters
st.sidebar.header("Filters")
selected_sales_reps = st.sidebar.multiselect("Select Sales Reps", options=[], default=[])

# Progress bar
progress_bar = st.progress(0)

# Fetch and filter data
def fetch_and_filter_data(saved_search_id, progress_value):
    progress_bar.progress(progress_value)
    
    # Fetch data from RESTlet
    df = fetch_restlet_data(saved_search_id)
    
    # Apply sales rep filter if selected
    if selected_sales_reps:
        df = df[df['Sales Rep'].isin(selected_sales_reps)]
    
    progress_bar.progress(progress_value + 25)
    return df

# Fetch data for both estimates and sales orders
estimate_data = fetch_and_filter_data("customsearch5127", 25)
sales_order_data = fetch_and_filter_data("customsearch5122", 50)

# Remove progress bar once the data is loaded
progress_bar.empty()

# Main top section with key metrics
st.header("Key Metrics")
st.columns(2)  # Create two columns for two metrics in each row
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        calculate_metrics(estimate_data, "estimates")
    with col2:
        calculate_metrics(sales_order_data, "sales_orders")

# Subtabs for Estimates and Sales Orders
st.header("Order Management")
tab1, tab2 = st.tabs(["Estimates", "Sales Orders"])

# Estimates tab
with tab1:
    st.subheader("Estimates")
    if not estimate_data.empty:
        st.dataframe(estimate_data)
    else:
        st.write("No data available for Estimates.")

# Sales Orders tab
with tab2:
    st.subheader("Sales Orders")
    if not sales_order_data.empty:
        st.dataframe(sales_order_data)
    else:
        st.write("No data available for Sales Orders.")
