
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

import streamlit as st
import pandas as pd
from utils.suiteql import fetch_suiteql_data_with_date_pagination

# Page Title
st.title("Inventory and Sales Data with Pagination")

# SuiteQL Queries for Inventory and Sales Data

inventory_query_template = """
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
AND item.createddate BETWEEN '{start_date}' AND '{end_date}'
ORDER BY 
    item_name ASC;
"""

sales_query_template = """
SELECT 
    transaction.internalid,
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
    AND transaction.trandate BETWEEN '{start_date}' AND '{end_date}'
ORDER BY 
    transaction.trandate DESC;
"""

# Fetch Inventory Data with Pagination (Unique key for button)
if st.button("Fetch Full Inventory Data", key="inventory_button"):
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    inventory_data = fetch_suiteql_data_with_date_pagination(inventory_query_template, start_date, end_date, step_days=30)
    if not inventory_data.empty:
        st.write("Inventory Data:")
        st.dataframe(inventory_data)
    else:
        st.error("No inventory data found.")

# Fetch Sales Data with Pagination (Unique key for button)
if st.button("Fetch Full Sales Data", key="sales_button"):
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    sales_data = fetch_suiteql_data_with_date_pagination(sales_query_template, start_date, end_date, step_days=30)
    if not sales_data.empty:
        st.write("Sales Data:")
        st.dataframe(sales_data)
    else:
        st.error("No sales data found.")
