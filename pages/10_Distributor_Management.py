import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Product Sync'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")



################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
from utils.restlet import fetch_restlet_data

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    df = fetch_restlet_data(saved_search_id)
    return df

# Fetch raw data for customsearch5135
st.write("Loading data with progress bar...")
customsearch5135_data_raw = fetch_raw_data("customsearch5135")

# Check if the data is not empty
if not customsearch5135_data_raw.empty:
    
    # Debugging: Check the column names
    st.write("Available columns:", customsearch5135_data_raw.columns)
    
    # Ensure the columns 'Distributor' and 'Amount' exist in the data
    if 'Distributor' in customsearch5135_data_raw.columns and 'Amount' in customsearch5135_data_raw.columns:
        # Aggregate sales via the 'Amount' column by 'Distributor' column
        aggregated_data = customsearch5135_data_raw.groupby('Distributor')['Amount'].sum().reset_index()
        # Apply currency formatting to the 'Amount' column in the Streamlit app
        customsearch5135_data_raw['Amount'] = customsearch5135_data_raw['Amount'].apply(lambda x: "${:,.2f}".format(x))

        # Display the aggregated data
        st.write("Aggregated Sales by Distributor:")
        st.dataframe(aggregated_data)
    else:
        st.error("Required columns 'Distributor' or 'Amount' not found in the data.")
    
    # Place the original DataFrame in an expander at the bottom of the page
    with st.expander("View Raw Data"):
        st.write("Original Data:")
        st.dataframe(customsearch5135_data_raw)

else:
    st.write("No data available for customsearch5135.")
