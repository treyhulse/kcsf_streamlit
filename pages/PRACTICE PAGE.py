import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

from utils.suiteql import fetch_suiteql_data

# Function to map the user's email to a customer ID
def get_customer_id_from_email(email):
    customer_map = {
        "treyhulse3@gmail.com": 4168611,  # Example mapping, adjust as needed
        # Add more email-to-customer mappings here
    }
    return customer_map.get(email, None)

# Function to fetch open sales orders using SuiteQL
def fetch_open_sales_orders(customer_id):
    query = f"""
    SELECT 
        tranid,
        type,
        entity,
        trandate,
        status
    FROM 
        transaction
    WHERE 
        entity = {customer_id}
    ORDER BY 
        trandate DESC;
    """
    
    return fetch_suiteql_data(query)

# Get the customer ID based on the logged-in email
customer_id = get_customer_id_from_email(user_email)

if customer_id:
    st.write(f"Fetching open sales orders for Customer ID: {customer_id}")
    
    # Fetch and display open sales orders
    open_sales_orders = fetch_open_sales_orders(customer_id)
    
    if not open_sales_orders.empty:
        st.write(f"Displaying open sales orders for {user_email}:")
        st.dataframe(open_sales_orders)
    else:
        st.write("No open sales orders found for this customer.")
else:
    st.error("Customer ID not found for this email.")
