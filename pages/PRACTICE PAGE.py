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

# Function to format currency
def format_currency(value):
    return "${:,.2f}".format(value) if pd.notna(value) else value

# Fetch data using the CSV-based RESTlet
def main():
    with st.spinner("Fetching Shipping Data..."):
        df = process_netsuite_data_csv(st.secrets["url_open_so"])

    # Remove 'Name' column
    if 'Name' in df.columns:
        df = df.drop(columns=['Name'])

    # Convert 'Order Number' to string
    df['Order Number'] = df['Order Number'].astype(str)

    # Convert 'Amount Remaining' to currency format
    df['Amount Remaining'] = df['Amount Remaining'].apply(format_currency)

    # Convert 'Ship Date' to datetime format
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])

    # Filter for weekdays (Monday to Friday)
    df = df[df['Ship Date'].dt.weekday < 5]

    # Apply mappings to relevant columns
    df['Ship Via'] = apply_mapping(df['Ship Via'], ship_via_mapping)
    df['Sales Rep'] = apply_mapping(df['Sales Rep'], sales_rep_mapping)
    df['Terms'] = apply_mapping(df['Terms'], terms_mapping)

    # Aggregate total orders by 'Ship Via' and display the count of orders by day
    aggregated_orders = df.groupby(['Ship Via', df['Ship Date'].dt.date]).size().reset_index(name='Total Orders')

    # Create a chart to visualize the orders by 'Ship Via' over time
    fig = px.line(
        aggregated_orders,
        x='Ship Date',
        y='Total Orders',
        color='Ship Via',
        title='Total Orders by Ship Via (Weekdays Only)'
    )

    # Display the chart and table in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Display aggregated data in a table
    st.write(aggregated_orders)

    # Option to download the filtered data
    csv = aggregated_orders.to_csv(index=False)
    st.download_button(
        label="Download aggregated data as CSV",
        data=csv,
        file_name="aggregated_orders_by_ship_via.csv",
        mime="text/csv",
    )

    # Display the modified DataFrame for debugging
    st.write("Modified DataFrame:")
    st.write(df)

if __name__ == "__main__":
    main()
