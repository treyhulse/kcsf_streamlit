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


from st_aggrid import AgGrid, GridOptionsBuilder
from utils.restlet import fetch_restlet_data
import time
import logging

# Set up logging to monitor the status
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to clear cache
def clear_cache():
    st.cache_data.clear()
    st.success("Cache cleared!")

# Button to clear cache
if st.button("Clear Cache"):
    clear_cache()

# Initialize Streamlit progress bar
progress_bar = st.progress(0)

# Fetch data using the RESTlet function
saved_search_id = 'customsearch5090'

# Cache only the data fetching part (returning a DataFrame)
@st.cache_data(ttl=86400)
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

    # Configure the AgGrid to display with pagination
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=100)  # Set page size to 50
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)

    gridOptions = gb.build()

    # Display the data in an interactive grid with pagination
    AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        theme='streamlit',  # Use valid theme
    )
else:
    logger.info("No data returned.")
    st.error("No data available or failed to load.")
