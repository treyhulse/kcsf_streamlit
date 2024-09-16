import streamlit as st
import pandas as pd
import logging
import traceback
from datetime import datetime, timedelta
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.data_functions import process_netsuite_data_csv
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping

# Configure page layout
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
    st.stop()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to check if a date is within this week
def is_within_this_week(date_str):
    try:
        date = pd.to_datetime(date_str, errors='coerce')
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of this week
        end_of_week = start_of_week + timedelta(days=6)  # Sunday of this week
        return start_of_week <= date <= end_of_week
    except Exception:
        return False

def apply_mappings(df):
    """Apply mappings to the DataFrame columns."""
    if 'Sales Rep' in df.columns:
        df['Sales Rep'] = df['Sales Rep'].map(sales_rep_mapping).fillna(df['Sales Rep'])
    
    if 'Ship Via' in df.columns:
        df['Ship Via'] = df['Ship Via'].map(ship_via_mapping).fillna(df['Ship Via'])
    
    if 'Terms' in df.columns:
        df['Terms'] = df['Terms'].map(terms_mapping).fillna(df['Terms'])

    return df

def format_dataframe(df):
    """Format 'Order Number' as string and 'Amount Remaining' as currency."""
    if 'Order Number' in df.columns:
        df['Order Number'] = df['Order Number'].astype(str)
    
    if 'Amount Remaining' in df.columns:
        df['Amount Remaining'] = df['Amount Remaining'].apply(lambda x: f"${x:,.2f}")
    
    return df

def apply_conditional_formatting(df):
    """Apply conditional formatting based on complex filters."""
    def evaluate_row(row):
        # Status filters
        good_status = row['status'] in ['SalesOrd:D', 'SalesOrd:B', 'SalesOrd:E'] and \
                      row['status'] not in ['BlankOrd:B', 'BlankOrd:H', 'BlankOrd:A', 'BlankOrd:R']
        
        # Quantity formula check: {quantity} - {quantityshiprecv} > 0
        good_quantity = row['quantity'] - row['quantityshiprecv'] > 0
        
        # Shipping must be 'F'
        good_shipping = row['shipping'] == 'F'
        
        # Taxline must be 'F'
        good_taxline = row['taxline'] == 'F'
        
        # Complex conditions
        good_complex_condition = (
            (row['total'] - row['custbody37'] <= 0) or
            (row['shipmethod'] in ['141', '148', '226']) or
            (row['customer.credithold'] in ['ON', 'OFF', 'AUTO'] and
             row['terms'] in ['5', '23', '21', '31', '22', '24', '6', '29', '28', '37', '30', '25', '7', '14', '1', '34',
                              '16', '2', '13', '3', '15', '8', '4', '35', '33', '32', '18', '38'])
        )
        
        # custbody219 must be within this week
        good_custom_body = is_within_this_week(row['custbody219'])
        
        # Combine all conditions
        is_good_to_go = all([good_status, good_quantity, good_shipping, good_taxline, good_complex_condition, good_custom_body])
        
        # Return styles: red text for rows that are not good to go
        return ['color: red'] * len(row) if not is_good_to_go else [''] * len(row)

    return df.style.apply(evaluate_row, axis=1)

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
            
            # Format 'Order Number' and 'Amount Remaining' columns
            df = format_dataframe(df)

            st.write(f"Data successfully fetched with {len(df)} records.")
            
            # Apply conditional formatting based on complex filters
            styled_df = apply_conditional_formatting(df)
            st.dataframe(styled_df)  # Display the styled DataFrame

            # Option to download the unformatted data as CSV
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
