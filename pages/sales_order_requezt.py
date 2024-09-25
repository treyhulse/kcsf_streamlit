import streamlit as st
from utils import make_netsuite_request

# Define the sales order internal ID
sales_order_id = 9318465

# Define the NetSuite RESTlet URL
url = f"{st.secrets['netsuite_base_url']}/app/site/hosting/restlet.nl?script=YOUR_SCRIPT_ID&deploy=YOUR_DEPLOY_ID&salesOrderId={sales_order_id}"

# Make the GET request
st.title("Sales Order Details")
sales_order_data = make_netsuite_request(url)

# Display the sales order data
if sales_order_data:
    st.json(sales_order_data)
