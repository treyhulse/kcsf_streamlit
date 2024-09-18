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

import streamlit as st
from utils.restlet import fetch_restlet_data
import pandas as pd

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Fetch raw data
open_order_data = fetch_raw_data("customsearch5065") 
pick_task_data = fetch_raw_data("customsearch5066") 

# Select only 'Order Number' and 'Task ID' from pick_task_data
pick_task_data = pick_task_data[['Order Number', 'Task ID']]

# Merge the two dataframes on 'Order Number', keeping all rows from open_order_data
merged_df = pd.merge(open_order_data, pick_task_data, on='Order Number', how='left')

# Display the merged dataframe in an expander section
with st.expander("View Merged Data"):
    st.write(merged_df)
