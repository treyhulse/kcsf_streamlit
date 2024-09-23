import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"Welcome, {user_email}. You have access to this page. This will show you all orders for this customer. I chose 90261 Spirit Halloween as your customer for example. We can adjust this mapping.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
from utils.suiteql import fetch_suiteql_data

# Function to map the user's email to a customer ID
def get_customer_id_from_email(email):
    customer_map = {
        "treyhulse3@gmail.com": 12762,  # Example mapping, adjust as needed
        "gina.bliss@kcstorefixtures.com": 12762,
        "jeff.smith@kcstorefixtures.com": 12762,

        # Add more email-to-customer mappings here
    }
    return customer_map.get(email, None)

# Functions to fetch data for different tabs using SuiteQL
def fetch_all_orders(customer_id):
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
        entity = {customer_id} AND status != 'Closed'
    ORDER BY 
        trandate DESC;
    """
    return fetch_suiteql_data(query)

def fetch_open_estimates(customer_id):
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
        entity = {customer_id} AND type = 'Estimate' AND status != 'Closed'
    ORDER BY 
        trandate DESC;
    """
    return fetch_suiteql_data(query)

def fetch_returns(customer_id):
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
        entity = {customer_id} AND type = 'Return Authorization'
    ORDER BY 
        trandate DESC;
    """
    return fetch_suiteql_data(query)

# Get the customer ID based on the logged-in email
customer_id = get_customer_id_from_email(user_email)

# Tab structure for the different views
if customer_id:
    st.write(f"Fetching data for Customer ID: {customer_id}.")
    
    # Create tabs for different views
    tabs = st.tabs(["All Orders", "Open Orders", "Open Estimates", "Returns"])

    with tabs[0]:
        st.subheader("All Orders")
        st.write(f"Displaying all orders for {user_email}:")
        all_orders = fetch_all_orders(customer_id)
        if not all_orders.empty:
            st.dataframe(all_orders)
        else:
            st.write("No orders found for this customer.")

    with tabs[1]:
        st.subheader("Open Orders")
        st.write(f"Displaying open sales orders for {user_email}:")
        open_sales_orders = fetch_open_sales_orders(customer_id)
        if not open_sales_orders.empty:
            st.dataframe(open_sales_orders)
        else:
            st.write("No open sales orders found for this customer.")
    
    with tabs[2]:
        st.subheader("Open Estimates")
        st.write(f"Displaying open estimates for {user_email}:")
        open_estimates = fetch_open_estimates(customer_id)
        if not open_estimates.empty:
            st.dataframe(open_estimates)
        else:
            st.write("No open estimates found for this customer.")
    
    with tabs[3]:
        st.subheader("Returns")
        st.write(f"Displaying return authorizations for {user_email}:")
        returns = fetch_returns(customer_id)
        if not returns.empty:
            st.dataframe(returns)
        else:
            st.write("No returns found for this customer.")
else:
    st.error("Customer ID not found for this email.")
