import streamlit as st
from utils.restlet import fetch_restlet_data
import pandas as pd

# Set the page title and layout
st.set_page_config(page_title="Manufacturing Insights", layout="wide")

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar header for additional controls or information if needed
st.sidebar.header("Manufacturing Wing Insights")

# Fetch raw data using the saved search ID "customsearch5162"
manufacturing_data_raw = fetch_raw_data("customsearch5162")

# Display the raw data as a dataframe
st.write("## Manufacturing Wing Data")
st.dataframe(manufacturing_data_raw)


