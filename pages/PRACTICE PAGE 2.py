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
from datetime import timedelta


# Cache the function to load data, resetting every hour
@st.cache_data(ttl=timedelta(hours=1))
def load_sales_data():
    client = None
    try:
        # Get MongoDB client
        client = get_mongo_client()
        # Fetch data from the 'salesLines' collection
        sales_data = get_collection_data(client, 'salesLines')
        
        # Drop duplicate rows to avoid the reindexing error
        sales_data = sales_data.drop_duplicates()
        
        # Check for necessary columns
        if 'Product Category' in sales_data.columns and 'Quantity' in sales_data.columns and 'Date' in sales_data.columns:
            # Convert 'Date' to datetime and 'Quantity' and 'Amount' to numeric
            sales_data['Date'] = pd.to_datetime(sales_data['Date'], errors='coerce')
            sales_data['Quantity'] = pd.to_numeric(sales_data['Quantity'], errors='coerce')
            if 'Amount' in sales_data.columns:
                sales_data['Amount'] = pd.to_numeric(sales_data['Amount'], errors='coerce')
            # Drop rows with NaN in essential columns
            sales_data = sales_data.dropna(subset=['Date', 'Quantity'])
            return sales_data
        else:
            st.write("Required columns ('Product Category', 'Quantity', 'Date') not found in the dataset.")
            return pd.DataFrame()  # Return empty DataFrame if columns are missing
    except Exception as e:
        st.error(f"Error fetching or processing data: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of errors
    finally:
        if client:
            client.close()

# Add a title to the Streamlit page
st.title("Supply Chain Data Overview")

# Progress bar for data load
progress_bar = st.progress(0)

# Load the sales data
progress_bar.progress(10)
sales_data = load_sales_data()
progress_bar.progress(50)

# Check if sales data is loaded and not empty
if not sales_data.empty:
    progress_bar.progress(80)

    # Single select dropdown to choose a product category
    selected_category = st.selectbox(
        'Select a Product Category', 
        options=sales_data['Product Category'].unique()
    )
    
    # Filter the data based on selected product category
    category_data = sales_data[sales_data['Product Category'] == selected_category]

    # Handle duplicates in the Date column by aggregating (e.g., summing quantities on the same date)
    category_data = category_data.groupby('Date').agg({
        'Quantity': 'sum',  # Sum quantities for the same date
        'Amount': 'sum',  # Sum amounts for the same date, if available
    }).reset_index()

    # Ensure the Date is sorted in ascending order to avoid the monotonic error
    category_data = category_data.sort_values(by='Date')

    # Group data by week and sum the 'Quantity'
    category_data.set_index('Date', inplace=True)
    weekly_data = category_data['Quantity'].resample('W').sum().reset_index()

    # Plot the weekly sales by product category with a line chart
    st.subheader(f"Weekly Sales for {selected_category}")
    st.line_chart(weekly_data.set_index('Date')['Quantity'], width=700, height=400, use_container_width=True)

    # Calculate the recommended quantity on hand (this could be based on the 90th percentile of quantity)
    recommended_quantity = category_data['Quantity'].quantile(0.90)
    st.metric("Recommended Quantity on Hand", f"{recommended_quantity:.2f}")

    # Display unique item count and total quantity in the selected category
    total_quantity = category_data['Quantity'].sum()
    st.metric("Total Quantity of Items", total_quantity)

    progress_bar.progress(100)
else:
    st.write("No data found or error fetching the data.")
