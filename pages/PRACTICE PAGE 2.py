import streamlit as st
import pandas as pd
import logging
import traceback
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.data_functions import process_netsuite_data_csv, replace_ids_with_display_values
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
    """Format 'Order Number' as string, 'Amount Remaining' as currency, and convert 'Warehouse' to string."""
    if 'Order Number' in df.columns:
        df['Order Number'] = df['Order Number'].astype(str)
    
    if 'Amount Remaining' in df.columns:
        df['Amount Remaining'] = df['Amount Remaining'].apply(lambda x: f"${x:,.2f}")
    
    if 'Warehouse' in df.columns:
        df['Warehouse'] = df['Warehouse'].astype(str)
    
    return df

def red_text_if_positive(df):
    """Set text to red in rows where 'Amount Remaining' is greater than 0,
    unless 'Ship Via' is 'Our Truck', 'Our Truck - Small', 'Our Truck - Large'
    or 'Terms' is 'Net 30', 'Net 60', 'Net 45'."""
    
    def red_text(row):
        # Check if 'Amount Remaining' is greater than 0
        if float(row['Amount Remaining'].replace('$', '').replace(',', '')) > 0:
            # Check for conditions to exclude rows from being red
            if row['Ship Via'] not in ['Our Truck', 'Our Truck - Small', 'Our Truck - Large'] and \
               row['Terms'] not in ['Net 30', 'Net 60', 'Net 45']:
                return ['color: red'] * len(row)
        return [''] * len(row)

    return df.style.apply(red_text, axis=1)

def main():
    st.title("NetSuite Data Fetcher")
    st.success("Data fetched from NetSuite")

    try:
        # Fetch Data from the RESTlet URL in Streamlit secrets
        df = process_netsuite_data_csv(st.secrets["url_open_so"])
        
        if df is None or df.empty:
            st.warning("No data retrieved from the NetSuite RESTlet.")
        else:
            # Apply the mappings (Sales Rep, Ship Via, Terms) to the DataFrame
            df = apply_mappings(df)
            
            # Format 'Order Number', 'Amount Remaining' columns, and convert 'Warehouse' to string
            df = format_dataframe(df)

            # Sidebar filters
            st.sidebar.title("Filters")

            # Sales Rep Filter
            sales_reps = ['All'] + df['Sales Rep'].unique().tolist()
            selected_sales_rep = st.sidebar.selectbox("Select Sales Rep", sales_reps, index=0)
            if selected_sales_rep != 'All':
                df = df[df['Sales Rep'] == selected_sales_rep]
            
            # Ship Date Filter
            min_date = pd.to_datetime(df['Ship Date']).min()
            max_date = pd.to_datetime(df['Ship Date']).max()
            date_range = st.sidebar.date_input("Select Ship Date Range", [min_date, max_date])
            if len(date_range) == 2:
                df = df[(pd.to_datetime(df['Ship Date']) >= pd.to_datetime(date_range[0])) &
                        (pd.to_datetime(df['Ship Date']) <= pd.to_datetime(date_range[1]))]

            st.write(f"Data successfully fetched with {len(df)} records.")
            
            # Apply conditional formatting to make rows with positive 'Amount Remaining' red text
            styled_df = red_text_if_positive(df)
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
