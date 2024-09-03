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

def apply_global_filters(df):
    st.sidebar.header("Global Filters")

    # Filter by Sales Rep
    sales_reps = ['All'] + df['Sales Rep'].unique().tolist()
    selected_sales_reps = st.sidebar.multiselect("Filter by Sales Rep", sales_reps, default='All')
    
    if 'All' not in selected_sales_reps:
        df = df[df['Sales Rep'].isin(selected_sales_reps)]

    # Filter by Status
    if 'Status' in df.columns:
        statuses = ['All'] + df['Status'].unique().tolist()
        selected_statuses = st.sidebar.multiselect("Filter by Status", statuses, default='All')
        if 'All' not in selected_statuses:
            df = df[df['Status'].isin(selected_statuses)]

    # Filter by Type
    if 'Type' in df.columns:
        types = ['All'] + df['Type'].unique().tolist()
        selected_types = st.sidebar.multiselect("Filter by Type", types, default='All')
        if 'All' not in selected_types:
            df = df[df['Type'].isin(selected_types)]

    # Ensure 'Date' is a datetime object
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Filter by Date (Admin)
        date_filter = st.sidebar.selectbox(
            "Filter by Date", 
            ["Custom", "This Month", "Today", "Tomorrow", "This Week", "Last Week", "Last Month", 
             "First Quarter", "Second Quarter", "Third Quarter", "Fourth Quarter", "Next Month"],
            index=0  # Default to "Custom"
        )

        today = datetime.today().date()

        if date_filter == "Today":
            start_date = today
            end_date = today
        elif date_filter == "Tomorrow":
            start_date = today + timedelta(days=1)
            end_date = start_date
        elif date_filter == "This Week":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif date_filter == "Last Week":
            start_date = today - timedelta(days=today.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif date_filter == "This Month":
            start_date = today.replace(day=1)
            next_month = start_date.replace(day=28) + timedelta(days=4)  # this will never fail
            end_date = next_month - timedelta(days=next_month.day)
        elif date_filter == "Last Month":
            first_day_this_month = today.replace(day=1)
            start_date = (first_day_this_month - timedelta(days=1)).replace(day=1)
            end_date = first_day_this_month - timedelta(days=1)
        elif date_filter == "First Quarter":
            start_date = datetime(today.year, 1, 1).date()
            end_date = datetime(today.year, 3, 31).date()
        elif date_filter == "Second Quarter":
            start_date = datetime(today.year, 4, 1).date()
            end_date = datetime(today.year, 6, 30).date()
        elif date_filter == "Third Quarter":
            start_date = datetime(today.year, 7, 1).date()
            end_date = datetime(today.year, 9, 30).date()
        elif date_filter == "Fourth Quarter":
            start_date = datetime(today.year, 10, 1).date()
            end_date = datetime(today.year, 12, 31).date()
        elif date_filter == "Next Month":
            first_day_next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
            start_date = first_day_next_month
            end_date = (first_day_next_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif date_filter == "Custom":
            start_date = st.sidebar.date_input("Start Date")
            end_date = st.sidebar.date_input("End Date")

            if start_date and not end_date:
                st.sidebar.error("Select an end date")
            elif end_date and not start_date:
                st.sidebar.error("Select a start date")

        # Apply date filter
        if start_date and end_date:
            df = df[(df['Date'] >= pd.to_datetime(start_date)) & 
                    (df['Date'] <= pd.to_datetime(end_date))]

    return df

# Main Streamlit app
st.title('Sales Dashboard')

# MongoDB Connection
client = get_mongo_client()
sales_data = get_collection_data(client, 'sales')

# Apply global filters
sales_data = apply_global_filters(sales_data)

# Layout with columns
col1, col2 = st.columns(2)

with col1:
    # Revenue by Sales Rep (Pie Chart)
    st.subheader('Revenue by Sales Rep')
    sales_rep_revenue = sales_data.groupby('Sales Rep')['Amount'].sum().reset_index()
    fig_pie = px.pie(sales_rep_revenue, names='Sales Rep', values='Amount', title='Revenue by Sales Rep')
    st.plotly_chart(fig_pie)

    # Sales by Category (Bar Graph)
    st.subheader('Sales by Category')
    sales_by_category = sales_data.groupby('Category')['Amount'].sum().reset_index()
    fig_bar = px.bar(sales_by_category, x='Category', y='Amount', title='Sales by Category')
    st.plotly_chart(fig_bar)

with col2:
    # Heatmap of Amount vs. Quantity
    if 'Quantity' in sales_data.columns:
        st.subheader('Heatmap of Amount vs. Quantity')
        fig_heatmap = px.density_heatmap(sales_data, x='Quantity', y='Amount', title='Heatmap of Amount vs. Quantity')
        st.plotly_chart(fig_heatmap)
    else:
        st.warning("Quantity column is missing. Please check the data.")

    # Pipeline of Steps Based on 'Status'
    st.subheader('Pipeline by Status')
    status_pipeline = sales_data.groupby('Status').size().reset_index(name='count')
    fig_pipeline = px.funnel(status_pipeline, x='Status', y='count', title='Pipeline by Status')
    st.plotly_chart(fig_pipeline)
