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

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar filters
st.sidebar.header("Filters")

# Fetch raw data for both estimates and sales orders
estimate_data_raw = fetch_raw_data("customsearch5127")
sales_order_data_raw = fetch_raw_data("customsearch5122")

# Extract unique sales reps from both datasets and add 'All' option
unique_sales_reps = pd.concat([estimate_data_raw['Sales Rep'], sales_order_data_raw['Sales Rep']]).dropna().unique()
unique_sales_reps = ['All'] + sorted(unique_sales_reps)  # Add 'All' as the first option

# Sales rep filter in the sidebar
selected_sales_reps = st.sidebar.multiselect("Select Sales Reps", options=unique_sales_reps, default=['All'])

# Apply the filter dynamically (not cached) to both datasets
def apply_filters(df):
    if selected_sales_reps and 'All' not in selected_sales_reps:
        df = df[df['Sales Rep'].isin(selected_sales_reps)]
    return df

estimate_data = apply_filters(estimate_data_raw)
sales_order_data = apply_filters(sales_order_data_raw)

# Function to calculate metrics for orders or estimates
def calculate_metrics(df):
    total_records = df.shape[0]
    ready_records = df[(df['Payment Status'].isin(['Paid', 'Terms'])) & (df['Stock Status'] == 'In Stock')].shape[0]
    not_ready_records = total_records - ready_records
    outstanding_revenue = df['Amount Remaining'].astype(float).sum()
    return total_records, ready_records, not_ready_records, outstanding_revenue

# Subtabs for Estimates and Sales Orders
st.header("Order Management")
tab1, tab2 = st.tabs(["Sales Orders", "Estimates"])

# Sales Orders tab
with tab1:
    st.subheader("Sales Orders")

    # Calculate metrics for sales orders
    total_orders, ready_orders, not_ready_orders, outstanding_revenue_orders = calculate_metrics(sales_order_data)

    # Display the metrics for Sales Orders
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Orders Ready", ready_orders)
    col3.metric("Total Orders Not Ready", not_ready_orders)
    col4.metric("Outstanding Revenue", f"${outstanding_revenue_orders:,.2f}")

    # Display the sales orders dataframe
    if not sales_order_data.empty:
        st.dataframe(sales_order_data)
    else:
        st.write("No data available for Sales Orders.")

# Estimates tab
with tab2:
    st.subheader("Estimates")

    # Calculate metrics for estimates
    total_estimates, ready_estimates, not_ready_estimates, outstanding_revenue_estimates = calculate_metrics(estimate_data)

    # Display the metrics for Estimates
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Estimates", total_estimates)
    col2.metric("Total Estimates Ready", ready_estimates)
    col3.metric("Total Estimates Not Ready", not_ready_estimates)
    col4.metric("Outstanding Revenue", f"${outstanding_revenue_estimates:,.2f}")

    # Display the estimates dataframe
    if not estimate_data.empty:
        st.dataframe(estimate_data)
    else:
        st.write("No data available for Estimates.")
