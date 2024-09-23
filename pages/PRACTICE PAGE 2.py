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
import time
import logging

# Set up logging to monitor the status
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Streamlit progress bar
progress_bar = st.progress(0)

# Fetch data using the RESTlet function
saved_search_id = 'customsearch5108'

# Log and display the status of data loading
st.write("Fetching data from NetSuite...")
logger.info(f"Fetching data for saved search ID: {saved_search_id}")
df = fetch_restlet_data(saved_search_id)

# Update progress bar to 50% once data is fetched
progress_bar.progress(50)
time.sleep(0.5)  # Simulate some delay for loading

# Check if DataFrame is not empty
if not df.empty:
    logger.info(f"Data fetched successfully with {len(df)} records.")

    # Display fetched data status
    st.success(f"Data successfully fetched! Total records: {len(df)}")

    # Configure the AgGrid to display with pagination
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)  # Set page size to 50
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)

    gridOptions = gb.build()

    # Update progress bar to 100% once grid is ready to display
    progress_bar.progress(100)
    time.sleep(0.5)  # Simulate some delay for rendering

    # Display the data in an interactive grid with pagination
    AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        theme='light',  # Can be 'light', 'dark', 'blue', etc.
    )

else:
    # Log the case where no data is returned
    logger.error("No data available or failed to load.")
    st.error("No data available for this saved search or failed to load.")

    # Update progress bar to 100% even on failure
    progress_bar.progress(100)
