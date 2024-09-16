import streamlit as st
import pandas as pd
import logging
import traceback
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.data_functions import process_netsuite_data_csv, replace_ids_with_display_values
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")

# User Authentication
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

page_name = 'Practice Page'  # Define the page name
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

def apply_mappings(df):
    """Apply mappings to the DataFrame columns."""
    if 'Sales Rep' in df.columns:
        df['Sales Rep'] = df['Sales Rep'].map(sales_rep_mapping).fillna(df['Sales Rep'])
    
    if 'Ship Via' in df.columns:
        df['Ship Via'] = df['Ship Via'].map(ship_via_mapping).fillna(df['Ship Via'])
    
    if 'Terms' in df.columns:
        df['Terms'] = df['Terms'].map(terms_mapping).fillna(df['Terms'])

    return df

def main():
    st.title("NetSuite Data Fetcher")
    st.success("Data fetched from NetSuite RESTlet")

    try:
        # Fetch Data from the RESTlet URL in Streamlit secrets
        df = process_netsuite_data_csv(st.secrets["url_open_so"])
        
        if df is None or df.empty:
            st.warning("No data retrieved from the NetSuite RESTlet.")
        else:
            # Apply the mappings (Sales Rep, Ship Via, Terms) to the DataFrame
            df = apply_mappings(df)
            
            st.write(f"Data successfully fetched with {len(df)} records.")
            st.dataframe(df)  # Display the DataFrame in a table format

            # Option to download data as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="netsuite_data.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Exception occurred: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("Please check the logs for more details.")

if __name__ == "__main__":
    main()
