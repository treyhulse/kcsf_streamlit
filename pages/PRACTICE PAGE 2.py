
import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Configure page layout
st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Order Management'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
import streamlit as st

@st.cache_data
def fetch_suiteql_data(query):
    # Function to fetch SuiteQL data; replace this with your actual query execution logic
    # This is a placeholder for the data fetching from NetSuite API.
    pass

# Inventory Query
inventory_query = """
SELECT 
    item.id AS item_id,
    item.itemid AS item_name,
    balance.location AS location_name,
    balance.quantityonhand AS quantity_on_hand,
    balance.quantityavailable AS quantity_available
FROM 
    item
JOIN 
    inventorybalance AS balance ON item.id = balance.item
WHERE 
    item.isinactive = 'F'
ORDER BY 
    item_name ASC;
"""

# Fetch inventory data
@st.cache_data
def get_inventory_data():
    inventory_data = fetch_suiteql_data(inventory_query)
    return pd.DataFrame(inventory_data)

# Sales Query
sales_query = """
SELECT 
    transaction.trandate,
    transaction.tranid,
    customer.entityid AS customer_name,
    item.itemid AS item_name,
    transactionline.quantity,
    transactionline.rate,
    transactionline.netamount AS line_total
FROM 
    transaction
JOIN 
    transactionline ON transaction.id = transactionline.transaction
JOIN 
    item ON transactionline.item = item.id
JOIN 
    customer ON transaction.entity = customer.id
WHERE 
    transaction.type = 'SalesOrd' 
    AND transaction.trandate >= TO_DATE('01/01/2023', 'MM/DD/YYYY')
ORDER BY 
    transaction.trandate DESC;
"""

# Fetch sales data
@st.cache_data
def get_sales_data():
    sales_data = fetch_suiteql_data(sales_query)
    return pd.DataFrame(sales_data)

# Load the data into dataframes
inventory_df = get_inventory_data()
sales_df = get_sales_data()

# Display the dataframes for manipulation or analysis
st.write("Inventory Data:")
st.dataframe(inventory_df)

st.write("Sales Data:")
st.dataframe(sales_df)
