import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Sales'  # Adjust this based on the current page
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
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

# Use st.cache_resource to cache the MongoDB client
@st.cache_resource(ttl=900)  # Set the time-to-live (ttl) to 900 seconds (15 minutes)
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
            index=6  # Default to "Custom"
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

def calculate_kpis(df):
    # Total Revenue for all 'Billed' orders
    total_revenue = df[df['Status'] == 'Billed']['Amount'].sum()

    # Average Order Volume for all 'Billed' orders
    average_order_volume = df[df['Status'] == 'Billed']['Amount'].mean()

    # Total Open Estimates (Count of unique document numbers for Estimate Type = Open)
    total_open_estimates = df[(df['Type'] == 'Estimate') & (df['Status'] == 'Open')]['Document Number'].nunique()

    # Total Open Orders (Count of unique document numbers for Sales Order Type != Billed or Closed)
    total_open_orders = df[(df['Type'] == 'Sales Order') & (~df['Status'].isin(['Billed', 'Closed']))]['Document Number'].nunique()

    return total_revenue, average_order_volume, total_open_estimates, total_open_orders

# Main Streamlit app
st.title('Sales Dashboard')

# MongoDB Connection
client = get_mongo_client()
sales_data = get_collection_data(client, 'sales')

# Apply global filters
sales_data = apply_global_filters(sales_data)

# Calculate KPIs
total_revenue, average_order_volume, total_open_estimates, total_open_orders = calculate_kpis(sales_data)

# Display KPIs in metric boxes
st.subheader('Key Performance Indicators')
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")

with col2:
    st.metric(label="Average Order Volume", value=f"${average_order_volume:,.2f}")

with col3:
    st.metric(label="Total Open Estimates", value=total_open_estimates)

with col4:
    st.metric(label="Total Open Orders", value=total_open_orders)

# Layout with columns for charts
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
    if 'Days Open' in sales_data.columns:
        st.subheader('Heatmap of Amount vs. Days Open')
        fig_heatmap = px.density_heatmap(sales_data, x='Days Open', y='Amount', title='Heatmap of Amount vs. Days Open')
        st.plotly_chart(fig_heatmap)
    else:
        st.warning("Quantity column is missing. Please check the data.")

    # Pipeline of Steps Based on 'Status'
    st.subheader('Pipeline by Status')
    status_pipeline = sales_data.groupby('Status').size().reset_index(name='count')
    fig_pipeline = px.funnel(status_pipeline, x='Status', y='count', title='Pipeline by Status')
    st.plotly_chart(fig_pipeline)

# Expandable AgGrid table at the bottom
with st.expander("View Data Table"):
    st.subheader("Sales Data")
    gb = GridOptionsBuilder.from_dataframe(sales_data)
    gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
    gridOptions = gb.build()

    grid_response = AgGrid(
        sales_data,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True,
        height=400, 
        width='100%',
        reload_data=True
    )
