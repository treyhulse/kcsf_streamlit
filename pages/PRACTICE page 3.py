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

# Fetch raw data for the new saved searches
sales_by_rep_data = fetch_raw_data("customsearch4963")
sales_by_category_data = fetch_raw_data("customsearch5145")
sales_by_month_data = fetch_raw_data("customsearch5146")

# Create a dictionary to store the dataframes and names
saved_searches = {
    "Sales by Sales Rep": sales_by_rep_data,
    "Sales by Category": sales_by_category_data,
    "Sales by Month": sales_by_month_data
}

# Display each saved search in a DataFrame
for search_name, df in saved_searches.items():
    st.header(search_name)
    st.dataframe(df)
    # Add a button to clear the cache
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared successfully!")