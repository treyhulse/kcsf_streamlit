import streamlit as st
import pandas as pd
import logging
import traceback
from utils.data_functions import process_netsuite_data_csv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")

def main():
    st.title("NetSuite Data Fetcher")
    st.success("Data fetched from NetSuite RESTlet")

    try:
        # Fetch Data from the RESTlet URL in Streamlit secrets
        df = process_netsuite_data_csv(st.secrets["url_open_so"])
        
        if df is None or df.empty:
            st.warning("No data retrieved from the NetSuite RESTlet.")
        else:
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
