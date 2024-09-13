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

import pandas as pd
from utils.data_functions import process_netsuite_data_csv
import streamlit as st

def main():
    st.header("Open Sales Orders Analysis")
    
    try:
        with st.spinner("Fetching Open Sales Orders..."):
            df_open_so = process_netsuite_data_csv(st.secrets["url_open_so"])
        st.success("Data loaded successfully!")
        
        # Display column names for debugging
        st.write("Available columns:", df_open_so.columns.tolist())
        
        # Display the dataframe
        st.write("Open Sales Orders Data:")
        st.dataframe(df_open_so)
        
        # Provide download option
        csv = df_open_so.to_csv(index=False)
        st.download_button(label="Download data as CSV", 
                           data=csv, 
                           file_name="open_sales_orders.csv", 
                           mime="text/csv")
    
    except Exception as e:
        st.error(f"Failed to fetch data: {str(e)}")

if __name__ == "__main__":
    main()