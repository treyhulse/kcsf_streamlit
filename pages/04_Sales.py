import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '04_Sales.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import logging
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

# Use st.cache_resource to cache the MongoDB client
@st.cache_resource
def get_mongo_client():
    try:
        logging.debug("Attempting to connect to MongoDB...")
        if "mongo_connection_string" not in st.secrets:
            raise ValueError("MongoDB connection string not found in secrets")
        
        connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
        client = MongoClient(connection_string, 
                             ssl=True,
                             serverSelectionTimeoutMS=30000,
                             connectTimeoutMS=30000,
                             socketTimeoutMS=30000)
        
        # Test the connection
        client.server_info()
        
        logging.info("MongoDB connection successful")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        st.error(f"Failed to connect to MongoDB: {e}")
        return None

# Main Streamlit app
st.title('Sales Dashboard')

# MongoDB Connection
client = get_mongo_client()

if client is None:
    st.error("Unable to connect to the database. Please check your connection and try again.")
    st.stop()

try:
    sales_data = get_collection_data(client, 'sales')
except Exception as e:
    st.error(f"Error fetching data from MongoDB: {e}")
    logging.error(f"Error fetching data from MongoDB: {e}")
    st.stop()

# Rest of your code remains the same...

# Apply global filters
sales_data = apply_global_filters(sales_data)

# Calculate KPIs
total_revenue, average_order_volume, total_open_estimates, total_open_orders = calculate_kpis(sales_data)

# ... (rest of the dashboard code)