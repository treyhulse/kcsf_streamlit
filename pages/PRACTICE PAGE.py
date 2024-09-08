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


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
from utils import fetch_suiteql_data

# Page Title
st.title('Inventory Check Page')

# Input field to get the item ID from the user
item_id = st.text_input('Enter Item ID', value='17842')

# SuiteQL query to fetch inventory data for the item
query = f"""
SELECT item, location, quantityonhand, quantityavailable 
FROM InventoryBalance 
WHERE item = {item_id}
"""

# When the user clicks the button, fetch data
if st.button('Check Inventory'):
    df = fetch_suiteql_data(query)
    
    if not df.empty:
        st.write(f"Inventory data for item ID: {item_id}")
        st.dataframe(df)
    else:
        st.error(f"No inventory data found for item ID {item_id}.")
