import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Supply Chain Data",
    page_icon="📊",
    layout="wide",
)

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

import pandas as pd
from utils.mongo_connection import get_mongo_client, get_collection_data

# Add a title to the Streamlit page
st.title("Supply Chain Data Overview")

# Connect to the MongoDB client and fetch data
st.write("Loading data from MongoDB...")

try:
    # Get MongoDB client
    client = get_mongo_client()
    
    # Fetch data from the 'salesLines' collection
    sales_data = get_collection_data(client, 'salesLines')

    # Check if the data has the necessary columns
    if 'Product Category' in sales_data.columns and 'Quantity' in sales_data.columns and 'Date' in sales_data.columns:
        
        # Convert the 'Date' column to a datetime format if it's not already
        sales_data['Date'] = pd.to_datetime(sales_data['Date'], errors='coerce')
        
        # Convert 'Quantity' and 'Amount' columns to numeric (handle errors by coercing to NaN)
        sales_data['Quantity'] = pd.to_numeric(sales_data['Quantity'], errors='coerce')
        if 'Amount' in sales_data.columns:
            sales_data['Amount'] = pd.to_numeric(sales_data['Amount'], errors='coerce')
        
        # Drop rows where Date is not valid or Quantity is NaN (optional step)
        sales_data = sales_data.dropna(subset=['Date', 'Quantity'])

        # Sort the data by Date for correct rolling calculations
        sales_data = sales_data.sort_values(by='Date')

        # Group by 'Product Category' and calculate the rolling 3-month average of 'Quantity'
        grouped_data = sales_data.groupby('Product Category').apply(
            lambda x: x.set_index('Date')['Quantity'].rolling(window='90D').mean()
        ).reset_index()

        # Plotting the rolling average for each product category
        st.subheader("Rolling 3-Month Average of Quantity by Product Category")

        # Streamlit's native line chart visualization
        categories = grouped_data['Product Category'].unique()
        
        # Loop through each category to plot
        for category in categories:
            category_data = grouped_data[grouped_data['Product Category'] == category]
            st.line_chart(category_data.set_index('Date')['Quantity'], width=700, height=400, use_container_width=True)

    else:
        st.write("Required columns ('Product Category', 'Quantity', 'Date') not found in the dataset.")
except Exception as e:
    st.error(f"Error fetching or processing data: {e}")

# Close the MongoDB connection when done
finally:
    if client:
        client.close()