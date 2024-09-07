import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Shipping Report'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
import plotly.express as px
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
    elif preset == "This Month":
        start_of_month = today.replace(day=1)
        end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return start_of_month, end_of_month
    else:
        return None, None

# Main function
def main():
    with st.spinner("Fetching Shipping Data..."):
        df = process_netsuite_data_csv(st.secrets["url_open_so"])

    # Apply necessary transformations
    df['Ship Date'] = pd.to_datetime(df['Ship Date']).dt.strftime('%m/%d/%Y')
    df['Order Number'] = df['Order Number'].astype(str)
    df['Amount Remaining'] = df['Amount Remaining'].apply(format_currency)

    # Map relevant columns
    df['Ship Via'] = apply_mapping(df['Ship Via'], ship_via_mapping)
    df['Sales Rep'] = apply_mapping(df['Sales Rep'], sales_rep_mapping)
    df['Terms'] = apply_mapping(df['Terms'], terms_mapping)

    # Filter Sidebar for Ship Via and Date Range
    st.sidebar.subheader("Select Ship Via")
    ship_vias = df['Ship Via'].unique().tolist()
    selected_ship_vias = st.sidebar.multiselect("Ship Via", ship_vias, default=ship_vias)

    st.sidebar.subheader("Select Date Range")
    date_preset = st.sidebar.selectbox("Select Date Range", ["This Week", "This Month"])
    start_date, end_date = get_date_range(date_preset)

    # Apply filters
    df_filtered = df[
        (df['Ship Via'].isin(selected_ship_vias)) &
        (pd.to_datetime(df['Ship Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(df['Ship Date']) <= pd.to_datetime(end_date))
    ]

    # Group by Ship Date and Ship Via
    grouped = df_filtered.groupby(['Ship Date', 'Ship Via']).size().reset_index(name='Total Orders')

    # Create a layout with 5 expandable columns (Monday through Friday)
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    days = pd.date_range(start=start_date, end=end_date, freq='B').strftime('%m/%d/%Y')  # Only business days

    st.header("Shipping Calendar")

    # Create 5 columns for Monday to Friday
    for day in days:
        # Get the orders for this specific day
        orders_today = grouped[grouped['Ship Date'] == day]

        if not orders_today.empty:
            with st.expander(f"{day} - Total Orders: {orders_today['Total Orders'].sum()}"):
                for _, row in orders_today.iterrows():
                    st.write(f"Ship Via: {row['Ship Via']}, Total Orders: {row['Total Orders']}")
        else:
            with st.expander(f"{day} - No shipments"):
                st.write("No orders for this day.")

if __name__ == "__main__":
    main()
