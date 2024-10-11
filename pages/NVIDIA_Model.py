import streamlit as st
from utils.restlet import fetch_restlet_data
import pandas as pd

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet
    return fetch_restlet_data(saved_search_id)

# Main Streamlit app function
def main():
    st.title('NetSuite Data Viewer')
    
    # Sidebar for user interactions
    st.sidebar.header("Filters")

    # Fetching data based on selected search
    data_raw = fetch_raw_data('customsearch5167')

    # Display data in the app
    if not data_raw.empty:
        st.write("Data Loaded Successfully:")
        st.dataframe(data_raw)
    else:
        st.write("No data available for the selected search.")

if __name__ == "__main__":
    main()
