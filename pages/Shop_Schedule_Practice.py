import streamlit as st
from utils.restlet import fetch_restlet_data
import pandas as pd

# Configure the Streamlit page layout
st.set_page_config(page_title="Manufacturing Data", layout="wide")

# Custom CSS to hide the Streamlit menu and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def fetch_raw_data(saved_search_id):
    # Fetch raw data from the specified NetSuite saved search ID
    df = fetch_restlet_data(saved_search_id)
    return df

# Fetch raw data using the saved search ID "customsearch5162"
manufacturing_data_raw = fetch_raw_data("customsearch5162")

# Display the fetched data as a DataFrame
st.write("## Manufacturing Wing Data")
st.dataframe(manufacturing_data_raw)

# Optional: Add any additional information, filters, or data processing as needed below
