import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
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

from utils.restlet import fetch_restlet_data
import pandas as pd
import streamlit as st

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar filters
st.sidebar.header("Filters")

# Fetch raw data for estimates, sales orders, customsearch5128, and customsearch5129
estimate_data_raw = fetch_raw_data("customsearch5127")
sales_order_data_raw = fetch_raw_data("customsearch5122")
customsearch5128_data_raw = fetch_raw_data("customsearch5128")
customsearch5129_data_raw = fetch_raw_data("customsearch5129")

# Extract unique sales reps from all datasets and add 'All' option
unique_sales_reps = pd.concat([
    estimate_data_raw['Sales Rep'], 
    sales_order_data_raw['Sales Rep'],
    customsearch5128_data_raw['Sales Rep'],
    customsearch5129_data_raw['Sales Rep']
]).dropna().unique()
unique_sales_reps = ['All'] + sorted(unique_sales_reps)  # Add 'All' as the first option

# Sales rep filter in the sidebar
selected_sales_reps = st.sidebar.multiselect("Select Sales Reps", options=unique_sales_reps, default=['All'])

# Apply the filter dynamically (not cached) to all datasets
def apply_filters(df):
    if selected_sales_reps and 'All' not in selected_sales_reps:
        df = df[df['Sales Rep'].isin(selected_sales_reps)]
    return df

estimate_data = apply_filters(estimate_data_raw)
sales_order_data = apply_filters(sales_order_data_raw)
customsearch5128_data = apply_filters(customsearch5128_data_raw)
customsearch5129_data = apply_filters(customsearch5129_data_raw)

# Function to calculate metrics for orders or estimates
def calculate_metrics(df):
    total_records = df.shape[0]
    ready_records = df[(df['Payment Status'].isin(['Paid', 'Terms'])) & (df['Stock Status'] == 'In Stock')].shape[0]
    not_ready_records = total_records - ready_records
    
    # Safely convert 'Amount Remaining' to float, handling non-numeric values
    df['Amount Remaining'] = pd.to_numeric(df['Amount Remaining'], errors='coerce').fillna(0)
    
    outstanding_revenue = df['Amount Remaining'].sum()
    return total_records, ready_records, not_ready_records, outstanding_revenue


# Function to apply conditional formatting to the 'Sales Order' column only
def highlight_conditions_column(s):
    if s['Payment Status'] == 'Needs Payment':
        return ['color: red' if col == 'Sales Order' else '' for col in s.index]
    elif s['Stock Status'] == 'Back Ordered':
        return ['color: orange' if col == 'Sales Order' else '' for col in s.index]
    return [''] * len(s)  # No formatting otherwise

# Subtabs for Estimates, Sales Orders, customsearch5128, and customsearch5129
st.header("Order Management")
tab1, tab2, tab3, tab4 = st.tabs(["Sales Orders", "Estimates", "Customsearch 5128", "Customsearch 5129"])

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

    # Apply conditional formatting to the 'Sales Order' column only
    if not sales_order_data.empty:
        styled_sales_order_data = sales_order_data.style.apply(highlight_conditions_column, axis=1)
        st.dataframe(styled_sales_order_data)
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

    # Apply conditional formatting to the 'Sales Order' column only
    if not estimate_data.empty:
        styled_estimate_data = estimate_data.style.apply(highlight_conditions_column, axis=1)
        st.dataframe(styled_estimate_data)
    else:
        st.write("No data available for Estimates.")

# Customsearch 5128 tab
with tab3:
    st.subheader("Customsearch 5128")

    # Calculate metrics for customsearch 5128 data
    total_customsearch5128, ready_customsearch5128, not_ready_customsearch5128, outstanding_revenue_customsearch5128 = calculate_metrics(customsearch5128_data)

    # Display the metrics for customsearch 5128 data
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customsearch 5128", total_customsearch5128)
    col2.metric("Total Customsearch 5128 Ready", ready_customsearch5128)
    col3.metric("Total Customsearch 5128 Not Ready", not_ready_customsearch5128)
    col4.metric("Outstanding Revenue", f"${outstanding_revenue_customsearch5128:,.2f}")

    # Apply conditional formatting to the 'Sales Order' column only
    if not customsearch5128_data.empty:
        styled_customsearch5128_data = customsearch5128_data.style.apply(highlight_conditions_column, axis=1)
        st.dataframe(styled_customsearch5128_data)
    else:
        st.write("No data available for Customsearch 5128.")

# Customsearch 5129 tab
with tab4:
    st.subheader("Customsearch 5129")

    # Calculate metrics for customsearch 5129 data
    total_customsearch5129, ready_customsearch5129, not_ready_customsearch5129, outstanding_revenue_customsearch5129 = calculate_metrics(customsearch5129_data)

    # Display the metrics for customsearch 5129 data
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customsearch 5129", total_customsearch5129)
    col2.metric("Total Customsearch 5129 Ready", ready_customsearch5129)
    col3.metric("Total Customsearch 5129 Not Ready", not_ready_customsearch5129)
    col4.metric("Outstanding Revenue", f"${outstanding_revenue_customsearch5129:,.2f}")

    # Apply conditional formatting to the 'Sales Order' column only
    if not customsearch5129_data.empty:
        styled_customsearch5129_data = customsearch5129_data.style.apply(highlight_conditions_column, axis=1)
        st.dataframe(styled_customsearch5129_data)
    else:
        st.write("No data available for Customsearch 5129.")
