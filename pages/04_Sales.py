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
from datetime import datetime, timedelta
import streamlit as st

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
        connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
        client = MongoClient(connection_string, 
                             ssl=True,
                             serverSelectionTimeoutMS=30000,
                             connectTimeoutMS=30000,
                             socketTimeoutMS=30000)
        logging.info("MongoDB connection successful")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise

def get_collection_data(client, collection_name):
    try:
        logging.debug(f"Fetching data from collection: {collection_name}")
        db = client['netsuite']  # Ensure the database name is correct
        collection = db[collection_name]
        
        data = []
        total_docs = collection.estimated_document_count()  # Get the total number of documents
        progress_bar = st.progress(0)  # Initialize the progress bar
        
        for i, doc in enumerate(collection.find()):
            try:
                # Process each document individually
                processed_doc = {}
                for key, value in doc.items():
                    if isinstance(value, str):
                        processed_doc[key] = value.encode('utf-8', 'ignore').decode('utf-8')
                    else:
                        processed_doc[key] = value
                data.append(processed_doc)
                
                # Update the progress bar
                progress_bar.progress((i + 1) / total_docs)
                
            except Exception as e:
                logging.error(f"Skipping problematic document {doc.get('_id', 'Unknown ID')}: {e}")
                continue  # Skip problematic document
        
        df = pd.DataFrame(data)

        # Remove the '_id' column if it exists
        if '_id' in df.columns:
            df.drop(columns=['_id'], inplace=True)

        logging.info(f"Data fetched successfully from {collection_name} with shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Error fetching data from collection {collection_name}: {e}")
        raise

# Main Streamlit app
st.title('Sales Dashboard')

# MongoDB Connection
client = get_mongo_client()
sales_data = get_collection_data(client, 'sales')

# Convert 'trandate' to datetime
sales_data['trandate'] = pd.to_datetime(sales_data['trandate'])

# Revenue by Sales Rep (Pie Chart)
st.subheader('Revenue by Sales Rep')
sales_rep_revenue = sales_data.groupby('sales_rep')['revenue'].sum().reset_index()
fig_pie = px.pie(sales_rep_revenue, names='sales_rep', values='revenue', title='Revenue by Sales Rep')
st.plotly_chart(fig_pie)

# Revenue This Month vs. Last Month (Line Graph)
st.subheader('Revenue This Month vs. Last Month')
this_month = sales_data[sales_data['trandate'].dt.month == datetime.now().month]
last_month = sales_data[sales_data['trandate'].dt.month == (datetime.now().month - 1)]
this_month_revenue = this_month.groupby(this_month['trandate'].dt.day)['revenue'].sum().reset_index()
last_month_revenue = last_month.groupby(last_month['trandate'].dt.day)['revenue'].sum().reset_index()
fig_line = px.line(this_month_revenue, x='trandate', y='revenue', title='Revenue This Month vs. Last Month')
fig_line.add_scatter(x=last_month_revenue['trandate'], y=last_month_revenue['revenue'], mode='lines', name='Last Month')
st.plotly_chart(fig_line)

# Sales by Category (Bar Graph)
st.subheader('Sales by Category')
sales_by_category = sales_data.groupby('category')['revenue'].sum().reset_index()
fig_bar = px.bar(sales_by_category, x='category', y='revenue', title='Sales by Category')
st.plotly_chart(fig_bar)

# Heatmap of Amount vs. Quantity
st.subheader('Heatmap of Amount vs. Quantity')
fig_heatmap = px.density_heatmap(sales_data, x='quantity', y='amount', title='Heatmap of Amount vs. Quantity')
st.plotly_chart(fig_heatmap)

# Pipeline of Steps Based on 'Status'
st.subheader('Pipeline by Status')
status_pipeline = sales_data.groupby('status').size().reset_index(name='count')
fig_pipeline = px.funnel(status_pipeline, x='status', y='count', title='Pipeline by Status')
st.plotly_chart(fig_pipeline)
