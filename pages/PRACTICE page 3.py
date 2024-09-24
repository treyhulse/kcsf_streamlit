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
    return fetch_restlet_data(saved_search_id)

# Fetch data (outside of the cache)
df = fetch_data(saved_search_id)

# Simulate progress updates (this part is not cached)
for i in range(5):
    progress_bar.progress((i+1)*20)
    time.sleep(0.1)

# Finalize progress
progress_bar.progress(100)

if not df.empty:
    st.success(f"Data fetched successfully with {len(df)} records.")
    
    # Define pagination variables
    page_size = 20  # Set page size
    total_pages = len(df) // page_size + (1 if len(df) % page_size != 0 else 0)

    # Pagination controls
    page_number = st.number_input('Page number', min_value=1, max_value=total_pages, value=1)
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size

    # Paginated DataFrame
    paginated_df = df.iloc[start_index:end_index]
    
    st.write(f"Displaying records {start_index + 1} to {min(end_index, len(df))} of {len(df)}")
    
    # Move the DataFrame into an expander at the bottom of the page
    with st.expander("Show DataFrame"):
        st.dataframe(paginated_df)

    # Calculate metrics for the dashboard
    billed_orders = df[df['Status'] == 'Billed']
    pending_orders = df[df['Status'] == 'Pending']
    closed_orders = df[df['Status'] == 'Closed']

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
    for metric in metrics:
        col = st.columns(1)[0]
        with col:
            st.markdown(f"<div class='metrics-box'><p class='metric-title'>{metric['label']}</p><p class='metric-value'>{metric['value']}</p></div>", unsafe_allow_html=True)

    # Visualization: Pie Chart
    fig_pie = px.pie(billed_orders, values='Amount', names='Sales Rep', title='Total Sales by Sales Rep')
    st.plotly_chart(fig_pie)

    # Visualization: Bar Chart
    fig_bar = px.bar(df, x='Category', y='Amount', title='Total Sales by Category')
    st.plotly_chart(fig_bar)

    # Visualization: Line Chart (compare this year vs last year)
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' is datetime type
    this_year = df[df['Date'].dt.year == pd.to_datetime('today').year]
    last_year = df[df['Date'].dt.year == pd.to_datetime('today').year - 1]

    this_year_weekly = this_year.resample('W', on='Date')['Amount'].sum()
    last_year_weekly = last_year.resample('W', on='Date')['Amount'].sum()

    fig_line = px.line(title='Weekly Sales Comparison')
    fig_line.add_scatter(x=this_year_weekly.index, y=this_year_weekly.values, mode='lines', name='This Year')
    fig_line.add_scatter(x=last_year_weekly.index, y=last_year_weekly.values, mode='lines', name='Last Year')
    st.plotly_chart(fig_line)

else:
    logger.info("No data returned.")
    st.error("No data available or failed to load.")
