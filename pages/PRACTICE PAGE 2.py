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

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from utils.restlet import fetch_restlet_data
import logging
import time
import pandas as pd

# Set up logging to monitor the status
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Streamlit progress bar
progress_bar = st.progress(0)

# Fetch data using the RESTlet function
saved_search_id = 'customsearch5108'

def fetch_data_with_progress(saved_search_id):
    try:
        # Fetch raw data from RESTlet
        logger.info(f"Fetching data for saved search ID: {saved_search_id}")
        df = fetch_restlet_data(saved_search_id)
        
        # Simulate progress
        for i in range(5):
            progress_bar.progress((i+1)*20)
            time.sleep(0.1)

        return df
    except Exception as e:
        logger.error(f"Error during data fetch: {e}")
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()  # Return empty DataFrame if an error occurs

# Fetch the data
df = fetch_data_with_progress(saved_search_id)

# Finalize progress
progress_bar.progress(100)

if not df.empty:
    st.success(f"Data fetched successfully with {len(df)} records.")

    # Configure the AgGrid to display with pagination
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)  # Set page size to 50
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)

    gridOptions = gb.build()

    # Ensure a valid theme for AgGrid
    AgGrid(
    df,
    gridOptions=gridOptions,
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True,
    theme='streamlit',  # Updated to a valid theme option
    )

else:
    logger.info("No data returned.")
    st.error("No data available or failed to load.")
