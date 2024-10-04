import streamlit as st
from utils.restlet import fetch_restlet_data
import pandas as pd

# Set up the Streamlit page configuration
st.set_page_config(page_title="Manufacturing Insights", layout="wide")

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    """
    Fetch raw data from the provided NetSuite saved search ID using the
    fetch_restlet_data function and return a DataFrame.
    """
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar for future controls or information display
st.sidebar.header("Manufacturing Wing Insights")

# Fetch the data using the saved search ID `customsearch5162`
manufacturing_data_raw = fetch_raw_data("customsearch5162")

# Check if the data is successfully fetched and not empty
if not manufacturing_data_raw.empty:
    # Display the raw data in a table format
    st.write("## Manufacturing Wing Data")
    st.dataframe(manufacturing_data_raw)

    # Optionally display basic statistics or summary
    st.write("### Summary Statistics")
    st.write(manufacturing_data_raw.describe())

    # Additional custom visualizations can go here
    # Example: st.bar_chart(manufacturing_data_raw["Column_Name"])

else:
    # Display a message if no data is available
    st.warning("No data available for the selected search ID.")
