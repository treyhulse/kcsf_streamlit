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
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping
from datetime import date, timedelta
import streamlit as st

# Function to apply mapping, but keep unmapped IDs as raw values
def apply_mapping(column, mapping_dict):
    return column.apply(lambda x: mapping_dict.get(x, x))

# Function to format currency
def format_currency(value):
    return "${:,.2f}".format(value) if pd.notna(value) else value

# Function to filter by date range
def get_date_range(preset):
    today = date.today()
    if preset == "Today":
        return today, today
    elif preset == "This Week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        return start_of_week, end_of_week
    elif preset == "Last Week":
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=4)
        return start_of_last_week, end_of_last_week
    elif preset == "This Month":
        start_of_month = today.replace(day=1)
        end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return start_of_month, end_of_month
    else:
        return None, None

# Main function
def main():
    st.header("Open Sales Orders Analysis")
    
    # Fetch Data
    try:
        with st.spinner("Fetching Open Sales Orders..."):
            df_open_so = process_netsuite_data_csv(st.secrets["url_open_so"])
        st.success("Data loaded successfully!")
    except Exception as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return

    # Display column names for debugging
    st.write("Available columns:", df_open_so.columns.tolist())

    # Apply mapping (with error handling)
    if 'Ship Via' in df_open_so.columns:
        df_open_so['Ship Via'] = df_open_so['Ship Via'].map(ship_via_mapping).fillna('Unknown')
    if 'Terms' in df_open_so.columns:
        df_open_so['Terms'] = df_open_so['Terms'].map(terms_mapping).fillna('Unknown')
    if 'Sales Rep' in df_open_so.columns:
        df_open_so['Sales Rep'] = df_open_so['Sales Rep'].map(sales_rep_mapping).fillna('Unknown')

    # Display filters
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Filter by Sales Rep")
        if 'Sales Rep' in df_open_so.columns:
            sales_reps = ['All'] + sorted(df_open_so['Sales Rep'].unique())
            selected_sales_reps = st.multiselect("Select Sales Reps", sales_reps, default=['All'])
        else:
            st.write("Sales Rep data not available")
            selected_sales_reps = ['All']

    with col2:
        st.subheader("Filter by Ship Via")
        if 'Ship Via' in df_open_so.columns:
            ship_vias = ['All'] + sorted(df_open_so['Ship Via'].unique())
            selected_ship_vias = st.multiselect("Select Ship Via", ship_vias, default=['All'])
        else:
            st.write("Ship Via data not available")
            selected_ship_vias = ['All']

    with col3:
        st.subheader("Filter by Ship Date")
        if 'Ship Date' in df_open_so.columns:
            date_preset = st.selectbox("Select date range preset", ["All", "Today", "This Week", "Last Week", "This Month"])
            
            if date_preset != "All":
                start_date, end_date = get_date_range(date_preset)
                st.write(f"Selected range: {start_date} to {end_date}")
            else:
                start_date, end_date = None, None
        else:
            st.write("Ship Date data not available")
            start_date, end_date = None, None

    # Apply filters
    filtered_df = df_open_so.copy()
    
    if 'All' not in selected_sales_reps and 'Sales Rep' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Sales Rep'].isin(selected_sales_reps)]
    
    if 'All' not in selected_ship_vias and 'Ship Via' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Ship Via'].isin(selected_ship_vias)]
    
    if start_date and end_date and 'Ship Date' in filtered_df.columns:
        filtered_df['Ship Date'] = pd.to_datetime(filtered_df['Ship Date'])
        filtered_df = filtered_df[(filtered_df['Ship Date'] >= pd.to_datetime(start_date)) & 
                                  (filtered_df['Ship Date'] <= pd.to_datetime(end_date))]

    # Display metrics
    total_orders = len(filtered_df)
    total_amount = filtered_df['Amount'].sum() if 'Amount' in filtered_df.columns else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Open Orders", total_orders)
    with col2:
        st.metric("Total Amount", f"${total_amount:,.2f}")

    # Data table and download option
    with st.expander("View Data Table"):
        st.write(f"Total records after filtering: {len(filtered_df)}")
        st.dataframe(filtered_df)
        csv = filtered_df.to_csv(index=False)
        st.download_button(label="Download filtered data as CSV", 
                           data=csv, 
                           file_name="filtered_sales_orders.csv", 
                           mime="text/csv")

if __name__ == "__main__":
    main()