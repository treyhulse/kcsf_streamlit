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
from utils.restlet import fetch_restlet_data
import pandas as pd

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar filters
st.sidebar.header("Saved Searches")

# Fetch raw data for each saved search
estimate_data_raw = fetch_raw_data("customsearch5127")
sales_order_data_raw = fetch_raw_data("customsearch5122")
customsearch5128_data_raw = fetch_raw_data("customsearch5128")
customsearch5129_data_raw = fetch_raw_data("customsearch5129")
quote_data_raw = fetch_raw_data("customsearch4993")

# Create a dictionary to store the dataframes and names
saved_searches = {
    "Estimate Data": estimate_data_raw,
    "Sales Order Data": sales_order_data_raw,
    "Custom Search 5128": customsearch5128_data_raw,
    "Custom Search 5129": customsearch5129_data_raw,
    "Quote Data": quote_data_raw
}

# Display each saved search in a DataFrame
for search_name, df in saved_searches.items():
    st.header(search_name)
    st.dataframe(df)
