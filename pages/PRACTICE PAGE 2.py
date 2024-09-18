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

# Cache the data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_and_filter_data(saved_search_id):
    # Fetch data from RESTlet
    df = fetch_restlet_data(saved_search_id)
    
    # Apply sales rep filter if selected and not 'All'
    if selected_sales_reps and 'All' not in selected_sales_reps:
        df = df[df['Sales Rep'].isin(selected_sales_reps)]
    
    return df

# Sidebar filters
st.sidebar.header("Filters")

# Fetch raw data for initializing sales rep filter
estimate_data = fetch_restlet_data("customsearch5127")
sales_order_data = fetch_restlet_data("customsearch5122")

# Extract unique sales reps from both datasets and add 'All' option
unique_sales_reps = pd.concat([estimate_data['Sales Rep'], sales_order_data['Sales Rep']]).dropna().unique()
unique_sales_reps = ['All'] + sorted(unique_sales_reps)  # Add 'All' as the first option

# Sales rep filter in the sidebar
selected_sales_reps = st.sidebar.multiselect("Select Sales Reps", options=unique_sales_reps, default=['All'])

# Progress bar
progress_bar = st.progress(0)

# Fetch data for both estimates and sales orders with caching
estimate_data = fetch_and_filter_data("customsearch5127")
progress_bar.progress(50)
sales_order_data = fetch_and_filter_data("customsearch5122")
progress_bar.progress(100)

# Remove progress bar once the data is loaded
progress_bar.empty()

# Function to calculate key metrics
def calculate_metrics(df, df_type):
    total_records = df.shape[0]
    outstanding_amount = df['Amount Remaining'].astype(float).sum()
    
    return total_records, outstanding_amount

# Main top section with key metrics
st.header("Order Management")
with st.container():
    col1, col2, col3, col4 = st.columns(4, gap="medium")  # Add gap to ensure proper spacing

    estimates_count, estimates_outstanding = calculate_metrics(estimate_data, "estimates")
    sales_orders_count, sales_orders_outstanding = calculate_metrics(sales_order_data, "sales_orders")
    
    # Add drop shadow effect to metric boxes
    metric_box_style = """
    <style>
    .metric-box {
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        padding: 15px;
        border-radius: 5px;
        background-color: white;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """
    st.markdown(metric_box_style, unsafe_allow_html=True)

    # Display the metrics with proper box layout
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Total Estimates Open", estimates_count)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("$ Outstanding from Estimates", f"${estimates_outstanding:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Total Sales Orders Open", sales_orders_count)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("$ Outstanding from Sales Orders", f"${sales_orders_outstanding:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

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
