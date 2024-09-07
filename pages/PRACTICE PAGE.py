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
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping  # Import mappings
from datetime import date, timedelta

# Function to apply mapping, but keep unmapped IDs as raw values
def apply_mapping(column, mapping_dict):
    return column.apply(lambda x: mapping_dict.get(x, x))  # If no mapping, return raw value

# Fetch data using the CSV-based RESTlet
def main():
    with st.spinner("Fetching Shipping Data..."):
        df = process_netsuite_data_csv(st.secrets["url_open_so"])

    # Convert 'Ship Date' to datetime format
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])

    # Filter for weekdays (Monday to Friday)
    df = df[df['Ship Date'].dt.weekday < 5]

    # Apply mappings to relevant columns
    df['Ship Via'] = apply_mapping(df['Ship Via'], ship_via_mapping)
    df['Sales Rep'] = apply_mapping(df['Sales Rep'], sales_rep_mapping)
    df['Terms'] = apply_mapping(df['Terms'], terms_mapping)

    # If you have mappings for 'Credit Status' or 'Payment Status', add them to mappings.py
    # Example (assuming you have these mappings):
    # df['Credit Status'] = apply_mapping(df['Credit Status'], credit_status_mapping)
    # df['Payment Status'] = apply_mapping(df['Payment Status'], payment_status_mapping)

    # Aggregation of total orders by 'Ship Via' and 'Ship Date'
    aggregated_orders = df.groupby(['Ship Via', df['Ship Date'].dt.date]).size().reset_index(name='Total Orders')

    # Plot the results in a line chart
    fig = px.line(
        aggregated_orders,
        x='Ship Date',
        y='Total Orders',
        color='Ship Via',
        title='Total Orders by Ship Via (Weekdays Only)'
    )

    # Display the chart and the DataFrame
    st.plotly_chart(fig, use_container_width=True)
    st.write(aggregated_orders)

    # Allow users to download the data
    csv = aggregated_orders.to_csv(index=False)
    st.download_button(
        label="Download aggregated data as CSV",
        data=csv,
        file_name="aggregated_orders_by_ship_via.csv",
        mime="text/csv",
    )

    # Display the full DataFrame for debugging
    st.write("Full DataFrame:")
    st.write(df)

if __name__ == "__main__":
    main()
