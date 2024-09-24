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
page_name = 'Distributor Management'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
from utils.suiteql import fetch_netsuite_inventory

# Title of the app
st.title("NetSuite Inventory Balance Data")

# Button to trigger data fetching
if st.button("Fetch Inventory Data"):
    st.write("Fetching data from NetSuite...")

    # Fetch the inventory balance data
    inventory_df = fetch_netsuite_inventory()

    if not inventory_df.empty:
        st.success(f"Successfully fetched {len(inventory_df)} records.")
        st.dataframe(inventory_df)  # Display the DataFrame in Streamlit

        # Option to download the data as CSV
        csv = inventory_df.to_csv(index=False)
        st.download_button(label="Download data as CSV", data=csv, file_name='inventory_data.csv', mime='text/csv')
    else:
        st.error("No data available or an error occurred during data fetching.")
