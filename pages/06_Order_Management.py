
import streamlit as st
import pandas as pd
import logging
import traceback
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.data_functions import process_netsuite_data_csv, replace_ids_with_display_values
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping
from datetime import datetime, timedelta

# Configure page layout
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
import plotly.express as px


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
customsearch5132_data_raw = fetch_raw_data("customsearch5132")
quote_data_raw = fetch_raw_data("customsearch4993")


# Extract unique sales reps from both datasets and add 'All' option
unique_sales_reps = pd.concat([
    estimate_data_raw['Sales Rep'], 
    sales_order_data_raw['Sales Rep'],
    customsearch5128_data_raw['Sales Rep'],
    customsearch5129_data_raw['Sales Rep']
]).dropna().unique()
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
customsearch5128_data = apply_filters(customsearch5128_data_raw)
customsearch5129_data = apply_filters(customsearch5129_data_raw)
customsearch5132_data = (customsearch5132_data_raw)
quote_data = (quote_data_raw)

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

################################################################################################
st.header("Order Management")

# Function to count the records for each funnel stage
def calculate_funnel_stages(estimates_df, sales_orders_df):
    # Count of Estimates Open
    estimates_open = estimates_df.shape[0]

    # Count of Sales Orders Pending Fulfillment
    pending_fulfillment = sales_orders_df[sales_orders_df['Status'].isin(['Pending Fulfillment'])].shape[0]

    # Count of Sales Orders Partially Fulfilled AND Pending Billing/Partially Fulfilled
    partially_fulfilled = sales_orders_df[sales_orders_df['Status'].isin(['Partially Fulfilled', 'Pending Billing/Partially Fulfilled'])].shape[0]

    # Count of Sales Orders Ready (Filtered by Stock Status = 'In Stock' AND Payment Status = 'Paid' or 'Terms')
    ready_orders = sales_orders_df[(sales_orders_df['Stock Status'] == 'In Stock') & 
                                   (sales_orders_df['Payment Status'].isin(['Paid', 'Terms']))].shape[0]

    return estimates_open, pending_fulfillment, partially_fulfilled, ready_orders

# Get the counts for each funnel stage
estimates_open, pending_fulfillment, partially_fulfilled, ready_orders = calculate_funnel_stages(estimate_data, sales_order_data)

# Funnel Chart Data
funnel_data = pd.DataFrame({
    'stage': ['Estimates Open', 'Pending Fulfillment', 'Partially Fulfilled / Pending Billing', 'Orders Ready'],
    'amount': [estimates_open, pending_fulfillment, partially_fulfilled, ready_orders]
})

# Funnel Chart using Plotly
st.subheader("Sales Pipeline Funnel")
funnel_chart = px.funnel(funnel_data, x='stage', y='amount', text='amount',  # Show amounts instead of conversion
                         color_discrete_sequence=['firebrick'])  # Set the color to red

# Customize the appearance
funnel_chart.update_traces(texttemplate='%{text}', textposition="inside")
funnel_chart.update_layout(title_text='Sales Pipeline Funnel', title_x=0.5)

# Add the funnel chart to Streamlit
st.plotly_chart(funnel_chart)


################################################################################################

# Subtabs for Estimates, Sales Orders, customsearch5128, and customsearch5129
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Sales Orders", "Estimates", "Purchase Orders", "Transfer Orders", "Work Orders"])

# Sales Orders tab (with metrics)
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

    # Apply conditional formatting and format 'Amount Remaining' as currency
    if not sales_order_data.empty:
        sales_order_data['Amount Remaining'] = sales_order_data['Amount Remaining'].apply(lambda x: f"${x:,.2f}")
        styled_sales_order_data = sales_order_data.style.apply(highlight_conditions_column, axis=1)
        st.dataframe(styled_sales_order_data)
    else:
        st.write("No data available for Sales Orders.")

# Estimates tab (with metrics)
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

    # Apply conditional formatting and format 'Amount Remaining' as currency
    if not estimate_data.empty:
        estimate_data['Amount Remaining'] = estimate_data['Amount Remaining'].apply(lambda x: f"${x:,.2f}")
        styled_estimate_data = estimate_data.style.apply(highlight_conditions_column, axis=1)
        st.dataframe(styled_estimate_data)
    else:
        st.write("No data available for Estimates.")


# Customsearch 5128 tab (no metrics)
with tab3:
    st.subheader("Purchase Orders")

    if not customsearch5128_data.empty:
        st.dataframe(customsearch5128_data)
    else:
        st.write("No data available for Customsearch 5128.")

# Customsearch 5129 tab (no metrics)
with tab4:
    st.subheader("Transfer Orders")

    if not customsearch5129_data.empty:
        st.dataframe(customsearch5129_data)
    else:
        st.write("No data available for Customsearch 5129.")


# Customsearch 5132 tab (no metrics)
with tab5:
    st.subheader("Work Orders")

    if not customsearch5132_data.empty:
        st.dataframe(customsearch5132_data)
    else:
        st.write("No data available for customsearch5132.")
