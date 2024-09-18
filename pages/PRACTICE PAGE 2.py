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

import streamlit as st
import pandas as pd
from utils.restlet import fetch_restlet_data

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar filters
st.sidebar.header("Filters")

# Fetch raw data for open orders and pick tasks
estimate_data_raw = fetch_raw_data("customsearch5065")
sales_order_data_raw = fetch_raw_data("customsearch5066")

# Merge the dataframes on 'Order Number'
merged_data = pd.merge(estimate_data_raw, sales_order_data_raw[['Order Number', 'Task ID']], 
                       on='Order Number', how='left')

# Add a checkbox to select all Sales Reps
all_sales_reps = st.sidebar.checkbox("Select All Sales Reps", value=True)
if all_sales_reps:
    # Select all sales reps if "Select All" is checked
    sales_rep_filter = merged_data['Sales Rep'].unique()
else:
    # Allow individual selection of sales reps
    sales_rep_filter = st.sidebar.multiselect("Select Sales Reps", options=merged_data['Sales Rep'].unique())

# Filter Ship Via (without default 'All')
ship_via_filter = st.sidebar.multiselect("Select Ship Via", options=merged_data['Ship Via'].unique())

# Custom date range filter
date_range_filter = st.sidebar.date_input("Select custom date range", [])

# Filter by Task ID options
show_tasked = st.sidebar.checkbox("Show rows with Task ID", value=True)
show_untasked = st.sidebar.checkbox("Show rows without Task ID", value=True)

# Apply filters

# Apply sales rep filter only if sales_rep_filter is not empty or 'Select All' is checked
if all_sales_reps or sales_rep_filter:
    merged_data = merged_data[merged_data['Sales Rep'].isin(sales_rep_filter)]

# Apply Ship Via filter
if ship_via_filter:
    merged_data = merged_data[merged_data['Ship Via'].isin(ship_via_filter)]

# Filter data based on Task ID
if not show_tasked:
    merged_data = merged_data[merged_data['Task ID'].isna()]
if not show_untasked:
    merged_data = merged_data[~merged_data['Task ID'].isna()]

# Main dashboard
st.title("Shipping Report")
st.write("You have access to this page.")

# Summary metrics
total_open_orders = merged_data.shape[0]
tasked_orders = merged_data[~merged_data['Task ID'].isna()].shape[0]
untasked_orders = merged_data[merged_data['Task ID'].isna()].shape[0]
successful_task_percentage = (tasked_orders / total_open_orders) * 100 if total_open_orders > 0 else 0

# Metrics display
st.metric("Total Open Orders", total_open_orders)
st.metric("Tasked Orders", tasked_orders)
st.metric("Untasked Orders", untasked_orders)
st.metric("Successful Task Percentage", f"{successful_task_percentage:.2f}%")

# Line chart for open sales orders by ship date
st.subheader("Open Sales Orders by Ship Date")
line_chart_data = merged_data.groupby('Ship Date')['Order Number'].count().reset_index()
st.line_chart(line_chart_data, x='Ship Date', y='Order Number')

# Pie chart for tasked vs untasked orders
st.subheader("Tasked vs Untasked Orders")
pie_chart_data = pd.DataFrame({
    'Orders': ['Tasked Orders', 'Untasked Orders'],
    'Count': [tasked_orders, untasked_orders]
})
st.pie_chart(pie_chart_data.set_index('Orders')['Count'])

# Expandable section for the raw dataframe
with st.expander("View Data Table"):
    st.dataframe(merged_data)
