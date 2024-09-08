# 10_Product_Sync.py
import streamlit as st
from utils.apis import fetch_all_data_csv, fetch_all_data_json

# Title of the page
st.title("NetSuite & Shopify Product Sync")

# Fetch data from the RESTlet URL provided in Streamlit secrets
url = st.secrets['url']  # The URL for the NetSuite RESTlet

# Display a spinner while fetching the data
with st.spinner("Fetching data from NetSuite..."):
    # You can choose between CSV or JSON depending on your RESTlet response
    data = fetch_all_data_json(url)  # Use fetch_all_data_csv if the RESTlet returns CSV

# Check if the data is successfully fetched
if not data.empty:
    st.success("Successfully fetched NetSuite data.")
    st.dataframe(data)  # Display the data as a DataFrame
else:
    st.error("No data available or failed to fetch data.")
