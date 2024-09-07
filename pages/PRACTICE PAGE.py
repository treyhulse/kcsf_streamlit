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
from utils.data_functions import process_netsuite_data_csv  # CSV fetcher
from datetime import date, timedelta

# Sales Rep mapping (unchanged)
sales_rep_mapping = {
    7: "Shelley Gummig",
    61802: "Kaitlyn Surry",
    4125270: "Becky Dean",
    4125868: "Roger Dixon",
    4131659: "Lori McKiney",
    47556: "Raymond Brown",
    4169685: "Shellie Pritchett",
    4123869: "Katelyn Kennedy",
    47708: "Phil Vaughan",
    4169200: "Dave Knudtson",
    4168032: "Trey Hulse",
    4152972: "Gary Bargen",
    4159935: "Derrick Lewis",
    66736: "Unspecified",
    67473: 'Jon Joslin',
}

# Ship Via mapping (unchanged)
ship_via_mapping = {
    141: "Our Truck",
    32356: "EPES - Truckload",
    226: "Pickup 2",
    36191: "Estes Standard",
    36: "Fed Ex Ground",
    3653: "Fed Ex Ground Home Delivery",
    7038: "Other - See Shipping Info",
    4: "UPS Ground",
    227: "Dayton Freight"
}

# Fetch data using the CSV-based RESTlet
def main():
    with st.spinner("Fetching Shipping Data..."):
        df = process_netsuite_data_csv(st.secrets["url_open_so"])

    # Convert 'Ship Date' to datetime format
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])

    # Filter for weekdays (Monday to Friday)
    df = df[df['Ship Date'].dt.weekday < 5]

    # Map 'Ship Via' column using the ship_via_mapping
    df['Ship Via'] = df['Ship Via'].map(ship_via_mapping).fillna('Unknown')

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

if __name__ == "__main__":
    main()
