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
import pandas as pd
from utils.restlet import fetch_restlet_data

@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar filters
st.sidebar.header("Filters")

def main():
    st.header("Fetch and Display Data")

    # Fetch raw data for both estimates and sales orders
    with st.progress("Fetching Open Order Data..."):
        estimate_data_raw = fetch_raw_data("customsearch5065")
        df_estimate = pd.DataFrame(estimate_data_raw)

    with st.progress("Fetching RF-Smart Task Data..."):
        sales_order_data_raw = fetch_raw_data("customsearch5066")
        df_sales_order = pd.DataFrame(sales_order_data_raw)

    # Display the dataframes
    st.subheader("Open Order Data")
    st.dataframe(df_estimate)

    st.subheader("RF-Smart Task Data")
    st.dataframe(df_sales_order)

if __name__ == "__main__":
    main()
