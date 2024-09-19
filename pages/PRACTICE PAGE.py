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

import streamlit as st
import pandas as pd
from utils.suiteql import fetch_suiteql_data, get_authentication

# A mock function to simulate customer ID retrieval based on email
def get_customer_id_from_email(user_email):
    customer_map = {
        "treyhulse3@gmail.com": 4168611,  # Example customer ID
        # Add more email-to-customer mappings here
    }
    return customer_map.get(user_email, None)

def fetch_open_sales_orders(customer_id):
    """
    Fetches open sales orders for a specific customer using SuiteQL.
    
    Args:
        customer_id (int): The internal customer ID.
    
    Returns:
        pd.DataFrame: DataFrame containing the open sales orders.
    """
    query = f"""
    SELECT
        tranid AS order_number,
        entity AS customer_id,
        trandate AS order_date,
        total AS order_total,
        status AS order_status
    FROM 
        transaction
    WHERE 
        entity = {customer_id} AND status = 'Open' 
    ORDER BY 
        trandate DESC
    """
    
    return fetch_suiteql_data(query)

# Page logic starts here
st.title("Customer Sales Orders")

# Assuming you have the logged-in user's email
logged_in_email = st.session_state.get('email', None)

if logged_in_email:
    customer_id = get_customer_id_from_email(logged_in_email)
    
    if customer_id:
        st.write(f"Fetching open sales orders for Customer ID: {customer_id}")
        
        # Fetch open sales orders for this customer
        open_sales_orders = fetch_open_sales_orders(customer_id)
        
        if not open_sales_orders.empty:
            st.write(f"Displaying open sales orders for {logged_in_email}:")
            st.dataframe(open_sales_orders)
        else:
            st.write("No open sales orders found for this customer.")
    else:
        st.error("Customer ID not found for this email.")
else:
    st.error("User is not logged in. Please log in to view your sales orders.")
