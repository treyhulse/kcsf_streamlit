import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Product Sync'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")



################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
from utils.restlet import fetch_restlet_data
import pandas as pd

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar filters (if needed for future extension)
st.sidebar.header("Filters")

# Fetch raw data for customsearch4966
customsearch4966_data_raw = fetch_raw_data("customsearch5135")

# Display data
if not customsearch4966_data_raw.empty:
    st.write("Displaying data for customsearch5135:")
    st.dataframe(customsearch4966_data_raw)
else:
    st.write("No data available for customsearch5135.")
