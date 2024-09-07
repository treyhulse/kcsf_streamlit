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
    elif preset == "Next Week":
        start_of_next_week = today + timedelta(days=(7 - today.weekday()))
        end_of_next_week = start_of_next_week + timedelta(days=4)
        return start_of_next_week, end_of_next_week
    elif preset == "This Month":
        start_of_month = today.replace(day=1)
        end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return start_of_month, end_of_month
    else:
        return None, None

# Main function
def main():
    # Adding custom CSS for green text in expanders
    st.markdown(
        """
        <style>
        .green-text {
            color: green;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
    ship_vias = ['All'] + df['Ship Via'].unique().tolist()
    selected_ship_vias = st.sidebar.multiselect("Ship Via", ship_vias, default=['All'])

    if 'All' in selected_ship_vias:
        selected_ship_vias = df['Ship Via'].unique().tolist()  # Select all if "All" is selected

    st.sidebar.subheader("Select Date Range")
    date_preset = st.sidebar.selectbox("Select Date Range", ["This Week", "Next Week", "This Month"])
    start_date, end_date = get_date_range(date_preset)

    # Apply filters
    df_filtered = df[
        (df['Ship Via'].isin(selected_ship_vias)) &
        (pd.to_datetime(df['Ship Date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(df['Ship Date']) <= pd.to_datetime(end_date))
    ]

    # Group by Ship Date and Ship Via
    grouped = df_filtered.groupby(['Ship Date', 'Ship Via']).size().reset_index(name='Total Orders')

    # Create 5 vertical columns (Monday through Friday)
    st.header("Shipping Calendar")
    cols = st.columns(5)

    # Mapping days of the week to columns
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    days = pd.date_range(start=start_date, end=end_date, freq='B').strftime('%m/%d/%Y')  # Only business days

    # Initialize the columns for Monday to Friday
    for i, day_name in enumerate(weekdays):
        with cols[i]:
            st.subheader(day_name)

            # Iterate over each date within the respective weekday
            for date_str in days:
                date_obj = pd.to_datetime(date_str)
                
                # Ensure only the correct weekday is shown in each column
                if date_obj.weekday() == i:
                    orders_today = df_filtered[df_filtered['Ship Date'] == date_str]

                    if not orders_today.empty:
                        total_orders = len(orders_today)
                        with st.expander(f"{date_str} - Total Orders: " + f"<span class='green-text'>{total_orders}</span>", expanded=False):
                            st.dataframe(orders_today)  # Display the DataFrame for that day
                    else:
                        with st.expander(f"{date_str} - No shipments"):
                            st.write("No orders for this day.")

if __name__ == "__main__":
    main()
