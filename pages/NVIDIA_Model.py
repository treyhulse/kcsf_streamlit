from utils.restlet import fetch_restlet_data
import pandas as pd
import streamlit as st

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache(ttl=900, show_spinner=False)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet
    return fetch_restlet_data(saved_search_id)

# Main Streamlit app function
def main():
    st.title('NetSuite Data Viewer')
    
    # Sidebar for user interactions
    st.sidebar.header("Filters")
    
    # Dropdown to select saved search
    search_option = st.sidebar.selectbox(
        "Select a saved search to load:",
        options=['customsearch5127', 'customsearch5167', 'customsearch5128', 'customsearch5129'],
        index=0  # Default selection
    )

    # Fetching data based on selected search
    data_raw = fetch_raw_data(search_option)

    # Display data in the app
    if not data_raw.empty:
        st.write("Data Loaded Successfully:")
        st.dataframe(data_raw)
    else:
        st.write("No data available for the selected search.")

if __name__ == "__main__":
    main()
