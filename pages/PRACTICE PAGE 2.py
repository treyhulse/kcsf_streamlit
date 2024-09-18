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
from utils.restlet import fetch_restlet_data
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Fetch raw data
open_order_data = fetch_raw_data("customsearch5065") 
pick_task_data = fetch_raw_data("customsearch5066") 

# Select only 'Order Number' and 'Task ID' from pick_task_data
pick_task_data = pick_task_data[['Order Number', 'Task ID']]

# Merge the two dataframes on 'Order Number', keeping all rows from open_order_data
merged_df = pd.merge(open_order_data, pick_task_data, on='Order Number', how='left')

# Convert 'Ship Date' to datetime format
merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'], errors='coerce')

# Sidebar filters
st.sidebar.header('Filters')

# Sales Rep filter with 'All' option
sales_rep_list = merged_df['Sales Rep'].unique().tolist()
sales_rep_list.insert(0, 'All')  # Add 'All' option to the beginning of the list

sales_rep_filter = st.sidebar.multiselect(
    'Sales Rep', 
    options=sales_rep_list, 
    default='All'
)

# Ship Date filter with custom range option
date_filter_options = ['Today', 'Past (including today)', 'Future', 'Custom Range']
ship_date_filter = st.sidebar.selectbox(
    'Ship Date',
    options=date_filter_options
)

if ship_date_filter == 'Custom Range':
    start_date = st.sidebar.date_input('Start Date', datetime.today() - timedelta(days=7))
    end_date = st.sidebar.date_input('End Date', datetime.today())
else:
    start_date = None
    end_date = None

# Tasked Orders checkbox
tasked_orders = st.sidebar.checkbox('Tasked Orders', value=True)

# Untasked Orders checkbox
untasked_orders = st.sidebar.checkbox('Untasked Orders', value=True)

# Apply Ship Date filter
today = pd.to_datetime(datetime.today())  # Ensure 'today' is in datetime format

if ship_date_filter == 'Today':
    merged_df = merged_df[merged_df['Ship Date'].dt.date == today.date()]  # Compare dates only
elif ship_date_filter == 'Past (including today)':
    merged_df = merged_df[merged_df['Ship Date'] <= today]
elif ship_date_filter == 'Future':
    merged_df = merged_df[merged_df['Ship Date'] > today]
elif ship_date_filter == 'Custom Range' and start_date and end_date:
    merged_df = merged_df[(merged_df['Ship Date'] >= pd.to_datetime(start_date)) & 
                          (merged_df['Ship Date'] <= pd.to_datetime(end_date))]

# Apply Sales Rep filter
if 'All' not in sales_rep_filter:
    merged_df = merged_df[merged_df['Sales Rep'].isin(sales_rep_filter)]

# Apply Tasked/Untasked Orders filter
if tasked_orders and not untasked_orders:
    merged_df = merged_df[merged_df['Task ID'].notna()]
elif untasked_orders and not tasked_orders:
    merged_df = merged_df[merged_df['Task ID'].isna()]

# Tab layout
tab1, tab2 = st.tabs(["Shipping Report", "Shipping Calendar"])

# Tab 1: Shipping Report
with tab1:
    # Metrics
    total_orders = len(merged_df)
    tasked_orders_count = merged_df['Task ID'].notna().sum()
    untasked_orders_count = merged_df['Task ID'].isna().sum()
    task_percentage = (tasked_orders_count / total_orders) * 100 if total_orders > 0 else 0

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Open Orders", total_orders)
    col2.metric("Tasked Orders", tasked_orders_count)
    col3.metric("Untasked Orders", untasked_orders_count)
    col4.metric("Successful Task Percentage", f"{task_percentage:.2f}%")

    # Display charts using Plotly
    if not merged_df.empty:
        col_chart, col_pie = st.columns([2, 1])
        with col_chart:
            merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'])
            ship_date_counts = merged_df['Ship Date'].value_counts().sort_index()
            fig_line = px.line(x=ship_date_counts.index, y=ship_date_counts.values, labels={'x': 'Ship Date', 'y': 'Number of Orders'}, title='Open Sales Orders by Ship Date')
            st.plotly_chart(fig_line, use_container_width=True)
        
        with col_pie:
            matched_orders = merged_df['Task ID'].notna().sum()
            unmatched_orders = merged_df['Task ID'].isna().sum()
            pie_data = pd.DataFrame({'Task Status': ['Tasked Orders', 'Untasked Orders'], 'Count': [matched_orders, unmatched_orders]})
            fig_pie = px.pie(pie_data, names='Task Status', values='Count', title='Tasked vs Untasked Orders', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.write("No data available for the selected filters.")

    # Display filtered DataFrame in an expander
    with st.expander("View Filtered Data Table"):
        st.write(merged_df)

# Tab 2: Shipping Calendar
with tab2:
    st.write("Shipping Calendar View")
    # Display the merged DataFrame
    st.write(merged_df)
