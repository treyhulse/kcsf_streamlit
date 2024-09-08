# 10_Product_Sync.py
import streamlit as st
from utils.apis import fetch_all_data_csv

# Title of the page
st.title("NetSuite & Shopify Product Sync")

# Fetch data from the RESTlet URL provided in Streamlit secrets
url = st.secrets['url']  # The URL for the NetSuite RESTlet

# Display a spinner while fetching the data
with st.spinner("Fetching data from NetSuite..."):
    # Fetch data from the RESTlet (CSV format)
    data = fetch_all_data_csv(url)

# Check if the data is successfully fetched
if not data.empty:
    st.success("Successfully fetched NetSuite data.")
    
    # Show the fetched data in a DataFrame
    st.dataframe(data)

    # Optionally, add download button for CSV
    csv = data.to_csv(index=False)
    st.download_button(label="Download as CSV", data=csv, file_name="netsuite_data.csv", mime="text/csv")
else:
    st.error("No data available or failed to fetch data.")
