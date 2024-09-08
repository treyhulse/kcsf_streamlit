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
st.title("Test SuiteQL Query")

# Simple query to fetch all records from the InventoryBalance table
query = "SELECT * FROM InventoryBalance LIMIT 10"

# Display the generated query
st.code(query, language="sql")

# Execute the query
if st.button("Run Test Query"):
    df = fetch_suiteql_data(query)
    
    if not df.empty:
        st.write(f"Results for your test query:")
        st.dataframe(df)
    else:
        st.error("No data found for your query.")
