import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

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
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
import streamlit as st
import plotly.express as px
from utils.restlet import fetch_restlet_data
import time
import logging

# Set up logging to monitor the status
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to clear cache
def clear_cache():
    st.cache.clear()
    st.success("Cache cleared!")

# Button to clear cache
if st.button("Clear Cache"):
    clear_cache()

# Initialize Streamlit progress bar
progress_bar = st.progress(0)

# Fetch data using the RESTlet function
saved_search_id = 'customsearch5108'

# Cache only the data fetching part (returning a DataFrame)
@st.cache(ttl=86400, allow_output_mutation=True)
def fetch_data(saved_search_id):
    logger.info(f"Fetching data for saved search ID: {saved_search_id}")
    data = fetch_restlet_data(saved_search_id)
    data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce')  # Convert 'Amount' to numeric
    data['Date'] = pd.to_datetime(data['Date'])  # Ensure 'Date' is datetime type
    return data

# Fetch data (outside of the cache)
df = fetch_data(saved_search_id)

# Sidebar filters for 'Sales Rep' and 'Date'
st.sidebar.header("Filter Data")
selected_rep = st.sidebar.multiselect("Select Sales Rep", options=pd.unique(df['Sales Rep']))
selected_date = st.sidebar.date_input("Select Date Range", [])

# Filter data based on sidebar selections
if selected_rep:
    df = df[df['Sales Rep'].isin(selected_rep)]
if selected_date:
    df = df[(df['Date'] >= selected_date[0]) & (df['Date'] <= selected_date[1])]

# Simulate progress updates (this part is not cached)
for i in range(5):
    progress_bar.progress((i+1)*20)
    time.sleep(0.1)

# Finalize progress
progress_bar.progress(100)

if not df.empty:
    st.success(f"Data fetched successfully with {len(df)} records.")
    
    # Calculate metrics for the dashboard
    billed_orders = df[df['Status'] == 'Billed']
    pending_orders = df[df['Status'] == 'Pending']
    closed_orders = df[(df['Status'] == 'Closed') & (~df['Closed Order Reason'].isin(['Items moved to a different order', 'Other - See Notes']))]

    total_revenue = billed_orders['Amount'].sum()
    average_order_volume = billed_orders['Amount'].mean()
    open_orders = len(pending_orders)
    lost_revenue = closed_orders['Amount'].sum()

    metrics = [
        {"label": "Total Revenue", "value": f"${total_revenue:,.2f}", "change": 0, "positive": True},  # No percentage change data available
        {"label": "Avg Order Volume", "value": f"${average_order_volume:,.2f}", "change": 0, "positive": True},
        {"label": "Open Orders", "value": open_orders, "change": 0, "positive": True},
        {"label": "Lost Revenue", "value": f"${lost_revenue:,.2f}", "change": 0, "positive": False}
    ]

    # Display metrics
    cols = st.columns(4)
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(f"<div class='metrics-box'><p class='metric-title'>{metric['label']}</p><p class='metric-value'>{metric['value']}</p></div>", unsafe_allow_html=True)

    # Visualization: Pie Chart (Top 12 Sales Reps)
    top_reps = billed_orders.groupby('Sales Rep')['Amount'].sum().nlargest(12).index
    top_reps_data = billed_orders[billed_orders['Sales Rep'].isin(top_reps)]
    fig_pie = px.pie(top_reps_data, values='Amount', names='Sales Rep', title='Total Sales by Top 12 Sales Reps')
    
    # Visualization: Bar Chart
    fig_bar = px.bar(df, x='Category', y='Amount', title='Total Sales by Category')
    
    # Visualization: Line Chart (compare this year vs last year)
    this_year = df[df['Date'].dt.year == pd.to_datetime('today').year]
    last_year = df[df['Date'].dt.year == pd.to_datetime('today').year - 1]

    this_year_weekly = this_year.resample('W', on='Date')['Amount'].sum()
    last_year_weekly = last_year.resample('W', on='Date')['Amount'].sum()

    fig_line = px.line(title='Weekly Sales Comparison')
    fig_line.add_scatter(x=this_year_weekly.index, y=this_year_weekly.values, mode='lines', name='This Year')
    fig_line.add_scatter(x=last_year_weekly.index, y=last_year_weekly.values, mode='lines', name='Last Year')
    
    # Arrange visualizations in two columns
    left_col, right_col = st.columns(2)
    with left_col:
        st.plotly_chart(fig_pie)
        st.plotly_chart(fig_bar)
    with right_col:
        st.plotly_chart(fig_line)

    with st.expander("View Filtered DataFrame"):
        st.dataframe(df)

else:
    logger.info("No data returned.")
    st.error("No data available or failed to load.")
