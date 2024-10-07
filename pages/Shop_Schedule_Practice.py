import streamlit as st
import pandas as pd
import altair as alt
from utils.restlet import fetch_restlet_data
# Set the page title
st.title("Distributor Management System")

# Cache the raw data fetching process with a 10-minute expiration
@st.cache_data(ttl=600)
def fetch_raw_data_with_progress(saved_search_id):
    # Initialize progress bar
    progress_bar = st.progress(0)
    
    # Simulating the data loading process in chunks
    df = fetch_restlet_data(saved_search_id)
    progress_bar.progress(33)  # 33% done after fetching data
    progress_bar.progress(100)  # 100% done
    progress_bar.empty()  # Remove progress bar when done
    return df

# Fetch raw data for customsearch5135 with progress bar
customsearch5135_data_raw = fetch_raw_data_with_progress("customsearch5163")
st.dataframe(customsearch5135_data_raw)