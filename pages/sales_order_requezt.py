import streamlit as st
from utils.rest import make_netsuite_rest_api_request

st.title("Fetch Sales Order from NetSuite API")

# Define the Sales Order internal ID
sales_order_id = 9318465

# Define the endpoint for the Sales Order record type and ID
endpoint = f"salesOrder/{sales_order_id}"

# Make the GET request to fetch the Sales Order
sales_order_data = make_netsuite_rest_api_request(endpoint)

# Display the Sales Order data
if sales_order_data:
    st.json(sales_order_data)
