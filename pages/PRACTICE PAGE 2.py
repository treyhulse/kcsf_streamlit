import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Supply Chain Data",
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

# Page title
st.title("Retrieve Saved Search Data")

# Input field for the Saved Search ID
saved_search_id = st.text_input("Enter the Saved Search ID (e.g., customsearch5122)")

# Fetch data when the Saved Search ID is provided
if saved_search_id:
    try:
        # Call the RESTlet to fetch the data
        data = fetch_restlet_data(saved_search_id)
        
        # Display the data in a DataFrame
        if not data.empty:
            st.dataframe(pd.DataFrame(data))
        else:
            st.write("No data available for the provided Saved Search ID.")
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
else:
    st.write("Please enter a Saved Search ID.")
