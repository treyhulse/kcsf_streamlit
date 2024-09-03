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

    # Ensure 'Ship Date (Admin)' is a datetime object
    if 'Ship Date (Admin)' in df.columns:
        df['Ship Date (Admin)'] = pd.to_datetime(df['Ship Date (Admin)'], errors='coerce')

        # Filter by Ship Date (Admin)
        date_filter = st.sidebar.selectbox(
            "Filter by Ship Date (Admin)", 
            ["This Month", "Today", "Tomorrow", "This Week", "Last Week", "Last Month", 
             "First Quarter", "Second Quarter", "Third Quarter", "Fourth Quarter", "Next Month"],
            index=0  # Default to "This Month"
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

        # Apply date filter
        df = df[(df['Ship Date (Admin)'] >= pd.to_datetime(start_date)) & 
                (df['Ship Date (Admin)'] <= pd.to_datetime(end_date))]

    return df

def create_visualizations(df):
    st.subheader("Create Your Own Visualizations")

    # Ensure that there are columns available for visualization
    if df.empty or df.shape[1] < 2:
        st.warning("Not enough data to create visualizations.")
        return

    # Select columns for X and Y axes
    x_column = st.selectbox("Select X-axis column", df.columns, index=df.columns.get_loc("Date") if "Date" in df.columns else 0)
    y_column = st.selectbox("Select Y-axis column", df.columns, index=df.columns.get_loc("Amount") if "Amount" in df.columns else 0)

    # Select the type of chart
    chart_type = st.selectbox("Select chart type", ["Bar", "Line", "Scatter", "Histogram", "Pie"])

    # Additional customizations
    chart_title = st.text_input("Chart Title", f"{chart_type} of {y_column} vs {x_column}")
    x_label = st.text_input("X-axis Label", x_column)
    y_label = st.text_input("Y-axis Label", y_column)
    color_column = st.selectbox("Color By", [None] + list(df.columns), index=0)
    
    # Create the chart based on user input
    if chart_type == "Bar":
        fig = px.bar(df, x=x_column, y=y_column, color=color_column, title=chart_title, labels={x_column: x_label, y_column: y_label})
    elif chart_type == "Line":
        fig = px.line(df, x=x_column, y=y_column, color=color_column, title=chart_title, labels={x_column: x_label, y_column: y_label})
    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x_column, y=y_column, color=color_column, title=chart_title, labels={x_column: x_label, y_column: y_label})
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x_column, color=color_column, title=chart_title, labels={x_column: x_label})
    elif chart_type == "Pie":
        fig = px.pie(df, names=x_column, values=y_column, title=chart_title)
    
    # Display the chart
    st.plotly_chart(fig)

def main():
    st.title("Data Visualization Tool")

    # Connect to MongoDB using the utility function
    client = get_mongo_client()

    # Load the 'sales' collection into a DataFrame
    data = get_collection_data(client, 'sales')

    # Apply global filters
    filtered_data = apply_global_filters(data)

    # Check if DataFrame is empty after filtering
    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        st.write(f"Number of Rows: {filtered_data.shape[0]}")
        
        # Create visualizations
        create_visualizations(filtered_data)

        # Collapsible section for the DataFrame with aggrid
        with st.expander("View Data"):
            gb = GridOptionsBuilder.from_dataframe(filtered_data)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_side_bar()
            grid_options = gb.build()

            AgGrid(
                filtered_data, 
                gridOptions=grid_options, 
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                theme="blue",
                update_mode="MODEL_CHANGED"
            )

if __name__ == "__main__":
    main()
