
import streamlit as st
import pandas as pd
import logging
import traceback
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.data_functions import process_netsuite_data_csv, replace_ids_with_display_values
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping
from datetime import datetime, timedelta

# Configure page layout
st.set_page_config(layout="wide")

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
            if row['Ship Via'] not in ['Our Truck', 'Our Truck - Small', 'Our Truck - Large', 'Pickup 1', 'Pickup 2'] and \
               row['Terms'] not in ['Net 30', 'is any of 1% 10 Net 30', '1% 10 Net 30 Firm', '1% 90 Net 91', '1%-10 Net 20', '1/2% 10 Net 11', '1/2% 10 Net 11 Firm', '2% 10 Net 30', '2% 10, Net 30 Firm', '2% 15 Net 30', 'Account Credit', 'Credit Card - Net 10', 'Credit Card - Net 30', 'Net 10', 'Net 10th', 'Net 15 Days NO CC', 'Net 15 Days YES CC', 'Net 28', 'Net 30', 'Net 45', 'Net 60', 'Net 7', 'Net 90', 'Net Invoice', 'Net Invoice - CC', 'Net-30 NO CC', 'Net-30 YES CC', 'No Charge', '2% 76 Net 77']:
                return ['color: red'] * len(row)
        return [''] * len(row)

    return df.style.apply(red_text, axis=1)

def get_date_ranges():
    """Define preset date ranges."""
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
    start_of_month = today.replace(day=1)
    end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)  # Last day of the month
    start_of_next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)

    date_options = {
        'Today': (today, today),
        'Last Week': (start_of_week - timedelta(days=7), start_of_week - timedelta(days=1)),
        'This Month': (start_of_month, end_of_month),
        'Next Month': (start_of_next_month, start_of_next_month + timedelta(days=32)),
        'All Time': (None, None),  # No filter
        'Custom': None  # Placeholder for custom date range
    }
    return date_options

def calculate_kpis(filtered_df):
    """Calculate metrics for the KPI boxes based on the filtered DataFrame."""
    total_orders = len(filtered_df)
    
    # Total Orders Not Ready (those with red text from conditional formatting)
    not_ready_orders = filtered_df.apply(lambda row: float(row['Amount Remaining'].replace('$', '').replace(',', '')) > 0 and 
                                row['Ship Via'] not in ['Our Truck', 'Our Truck - Small', 'Our Truck - Large', 'Pickup 1', 'Pickup 2'] and 
                                row['Terms'] not in ['Net 30', 'Net 60', 'Net 45'], axis=1)
    total_orders_not_ready = not_ready_orders.sum()

    # Total Orders Ready (those not in red text)
    total_orders_ready = total_orders - total_orders_not_ready

    # Total Revenue Outstanding for orders not ready
    total_revenue_outstanding = filtered_df[not_ready_orders]['Amount Remaining'].apply(lambda x: float(x.replace('$', '').replace(',', ''))).sum()

    return total_orders, total_orders_ready, total_orders_not_ready, total_revenue_outstanding

def main():
    st.title("Order Management")
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

            # Sales Rep Multiselect Filter
            sales_reps = df['Sales Rep'].unique().tolist()
            selected_sales_reps = st.sidebar.multiselect("Select Sales Rep(s)", ['All'] + sales_reps, default=['All'])
            if 'All' not in selected_sales_reps:
                df = df[df['Sales Rep'].isin(selected_sales_reps)]

            # Ship Date Filter with Preset Ranges
            date_options = get_date_ranges()
            date_selection = st.sidebar.selectbox("Select Ship Date Range", list(date_options.keys()), index=4)  # Default to 'All Time'

            if date_selection == 'Custom':
                custom_range = st.sidebar.date_input("Select Custom Date Range", [datetime.today(), datetime.today()])
                if len(custom_range) == 2:
                    df = df[(pd.to_datetime(df['Ship Date']) >= pd.to_datetime(custom_range[0])) &
                            (pd.to_datetime(df['Ship Date']) <= pd.to_datetime(custom_range[1]))]
            else:
                start_date, end_date = date_options[date_selection]
                if start_date and end_date:
                    df = df[(pd.to_datetime(df['Ship Date']) >= start_date) &
                            (pd.to_datetime(df['Ship Date']) <= end_date)]

            # After filters are applied, recalculate KPI metrics
            total_orders, total_orders_ready, total_orders_not_ready, total_revenue_outstanding = calculate_kpis(df)

            # Display KPI metric boxes
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Orders", total_orders)
            col2.metric("Total Orders Ready", total_orders_ready)
            col3.metric("Total Orders Not Ready", total_orders_not_ready)
            col4.metric("Total Revenue Outstanding", f"${total_revenue_outstanding:,.2f}")

            st.write(f"{len(df)} records.")
            
            # Apply conditional formatting to make rows with positive 'Amount Remaining' red text
            styled_df = red_text_if_positive(df)
            st.dataframe(styled_df)  # Display the styled DataFrame

            # Option to download the unformatted data as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="order_management.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Exception occurred: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("Please check the logs for more details.")

if __name__ == "__main__":
    main()
