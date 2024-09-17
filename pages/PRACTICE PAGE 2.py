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

import pandas as pd
from utils.mongo_connection import get_mongo_client, get_collection_data

# Add a title to the Streamlit page
st.title("Supply Chain Data Overview")

# Connect to the MongoDB client and fetch data
st.write("Loading data from MongoDB...")

try:
    # Get MongoDB client
    client = get_mongo_client()
    
    # Fetch data from the 'salesLines' collection
    sales_data = get_collection_data(client, 'salesLines')
    
    # Display the data in a Streamlit table
    if not sales_data.empty:
        st.write(f"Displaying {len(sales_data)} records from the 'salesLines' collection.")
        st.dataframe(sales_data)  # Streamlit's dataframe for better visualization
    else:
        st.write("No data found in the 'salesLines' collection.")
except Exception as e:
    st.error(f"Error fetching data: {e}")

# Close the MongoDB connection when done
finally:
    if client:
        client.close()
