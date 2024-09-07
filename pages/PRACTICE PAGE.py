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
from utils.data_functions import process_netsuite_data_json
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

# Fetch data using the NetSuite RESTlet (replacing CSV fetching with JSON)
def main():
    with st.spinner("Fetching Shipping Data..."):
        df = process_netsuite_data_json(st.secrets["url_open_so"], sales_rep_mapping)

    # Display the DataFrame structure for debugging
    st.write("Columns in the DataFrame:")
    st.write(df.columns)  # This will print the DataFrame's column headers
    
    st.write("First 5 rows of the DataFrame:")
    st.write(df.head())  # This will display the first 5 rows of the DataFrame for inspection

    # Ensure you don't run any further processing until you've confirmed the column names.
    st.stop()  # Stop the execution to inspect the columns and data before proceeding

if __name__ == "__main__":
    main()
