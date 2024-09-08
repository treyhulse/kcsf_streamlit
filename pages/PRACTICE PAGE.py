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
from utils.suiteql import fetch_suiteql_data

# Page Title
st.title("Item ID Search")

# Input for Item ID (required)
item_filter = st.text_input("Enter Item ID (Required)", value="")

# Build the SuiteQL query to search by itemid
if item_filter:
    query = f"SELECT itemid, displayname FROM InventoryItem WHERE itemid = '{item_filter}' LIMIT 10"
else:
    query = "SELECT itemid, displayname FROM InventoryItem LIMIT 10"

# Display the generated query
st.code(query, language="sql")

# Execute the query
if st.button("Run Query"):
    df = fetch_suiteql_data(query)
    
    if not df.empty:
        st.write(f"Results for Item ID: {item_filter}")
        st.dataframe(df)
    else:
        st.error(f"No data found for Item ID: {item_filter}")
