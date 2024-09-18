import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

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

from utils.restlet import fetch_restlet_data
import pandas as pd

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar filters
st.sidebar.header("Filters")

# Fetch raw data for open orders and pick tasks
estimate_data_raw = fetch_raw_data("customsearch5065")
sales_order_data_raw = fetch_raw_data("customsearch5066")

# Merge the dataframes on the 'Sales Order' column
# Assuming the column that holds the sales order number is named 'Sales Order' in both dataframes
merged_data = pd.merge(estimate_data_raw, sales_order_data_raw[['Order Number', 'Task ID']], 
                       on='Order Number', how='left')

# Display the raw data
st.subheader("Merged Order and Pick Task Data")
st.dataframe(merged_data)
