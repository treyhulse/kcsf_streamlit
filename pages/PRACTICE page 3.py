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
import pandas as pd
from utils.restlet import fetch_restlet_data  # Adjust this to the correct import path if needed

# Cache the raw data fetching process
@st.cache_data(ttl=900)  # Cache for 15 minutes to avoid multiple calls
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Header for the page
st.header("NetSuite Saved Search Data")

# Fetch data from the saved search
saved_search_id = "customsearch4993"  # Replace with your saved search ID
quote_data_raw = fetch_raw_data(saved_search_id)

# Debug: Show the raw data as it comes in
st.write("Raw Data from RESTlet:")
st.write(quote_data_raw)

# Ensure the data contains the expected columns, otherwise show an error
if quote_data_raw is not None and not quote_data_raw.empty:
    # Ensure that all three columns ('Document Number', 'Latest', 'Earliest') are present
    if set(['Document Number', 'Latest', 'Earliest']).issubset(quote_data_raw.columns):
        # Display the dataframe
        st.write("Formatted Data:")
        st.dataframe(quote_data_raw[['Document Number', 'Latest', 'Earliest']])
    else:
        st.error("The expected columns are not present in the data.")
else:
    st.error("No data fetched from the RESTlet.")
