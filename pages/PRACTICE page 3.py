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

# Check user email for cache clear button
if user_email in ["treyhulse3@gmail.com", "trey.hulse@kcstorefixtures.com"]:
    if st.button("Clear Cache"):
        st.cache.clear()
        st.success("Cache cleared!")

################################################################################################

## AUTHENTICATED

################################################################################################


import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import time
import logging

# Set up logging to monitor the status
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the page configuration
st.set_page_config(page_title="Practice Page", page_icon="📊", layout="wide")

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
page_name = 'Practice Page'
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"Welcome, {user_email}. You have access to this page.")

# Clear Cache Button visible only to specific users
if user_email in ["treyhulse3@gmail.com", "trey.hulse@kcstorefixtures.com"]:
    if st.button("Clear Cache"):
        st.caching.clear_cache()
        st.success("Cache cleared!")

# Initialize Streamlit progress bar
progress_bar = st.progress(0)

# Fetch data using the RESTlet function
saved_search_id = 'customsearch5108'

@st.cache(ttl=86400, allow_output_mutation=True)
def fetch_data(saved_search_id):
    logger.info(f"Fetching data for saved search ID: {saved_search_id}")
    data = fetch_restlet_data(saved_search_id)
    data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce')
    data['Date'] = pd.to_datetime(data['Date'])
    return data

df = fetch_data(saved_search_id)

# Sidebar filters for 'Sales Rep' and 'Date'
st.sidebar.header("Filter Data")
all_reps = ['All'] + sorted(pd.unique(df['Sales Rep']))
selected_rep = st.sidebar.multiselect("Select Sales Rep", options=all_reps, default='All')
selected_date = st.sidebar.date_input("Select Date Range", [])

# Apply filters to data
if 'All' not in selected_rep:
    df = df[df['Sales Rep'].isin(selected_rep)]
if selected_date:
    df = df[(df['Date'] >= selected_date[0]) & (df['Date'] <= selected_date[1])]

# Simulate progress updates
for i in range(5):
    progress_bar.progress((i+1)*20)
    time.sleep(0.1)
progress_bar.progress(100)

# Display data if available
if not df.empty:
    st.success(f"Data fetched successfully with {len(df)} records.")
    # Calculate metrics
    ...

    # Improved metric boxes styling
    st.markdown("""
        <style>
        .metrics-box {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .metric-title { font-size: 20px; margin: 0; }
        .metric-value { font-size: 28px; margin: 0; font-weight: bold; }
        .metric-change { font-size: 14px; margin: 0; }
        </style>
    """, unsafe_allow_html=True)
    ...
    
    # Visualization logic here
    ...

    # Display DataFrame at the bottom in an expander
    with st.expander("View Detailed Data"):
        st.dataframe(df)

else:
    logger.info("No data returned.")
    st.error("No data available or failed to load.")
