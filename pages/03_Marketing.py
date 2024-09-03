import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '03_Marketing.py'  # Adjust this based on the current page
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
            elif start_date and end_date:
                if start_date > end_date:
                    st.sidebar.error("Start date must be before end date")

        # Apply date filter if start_date and end_date are defined
        if 'start_date' in locals() and 'end_date' in locals():
            if isinstance(start_date, datetime) or isinstance(start_date, pd.Timestamp):
                start_date = pd.to_datetime(start_date).date()
            if isinstance(end_date, datetime) or isinstance(end_date, pd.Timestamp):
                end_date = pd.to_datetime(end_date).date()
            df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    return df

def save_visualization(client, user_email, chart_name, chart_type, x_column, y_column, color_column, chart_title, x_label, y_label):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        
        chart_data = {
            "name": chart_name,
            "user": user_email,  # Store the user's email
            "type": chart_type,
            "x_column": x_column,
            "y_column": y_column,
            "color_column": color_column,
            "chart_title": chart_title,
            "x_label": x_label,
            "y_label": y_label,
            "created_at": datetime.utcnow()
        }

        charts_collection.insert_one(chart_data)
        st.success(f"Visualization '{chart_name}' saved successfully by {user_email}.")
    except Exception as e:
        st.error(f"Failed to save visualization: {e}")
        logging.error(f"Failed to save visualization: {e}")

def load_visualizations(client):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        
        return list(charts_collection.find())
    except Exception as e:
        st.error(f"Failed to load visualizations: {e}")
        logging.error(f"Failed to load visualizations: {e}")
        return []

def create_visualizations(df, client):
    st.subheader("Create Your Own Visualizations")

    # Ensure that there are columns available for visualization
    if df.empty or df.shape[1] < 2:
        st.warning("Not enough data to create visualizations.")
        return

    # Initialize session state variables for chart details
    if 'chart_details' not in st.session_state:
        st.session_state.chart_details = {}

    # Form for visualization creation
    with st.form(key='visualization_form'):
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

        # Preview button
        preview_button = st.form_submit_button("Preview Visualization")

    # If the user clicks "Preview Visualization"
    if preview_button:
        # Store the chart details in session state to retain data after preview
        st.session_state.chart_details = {
            "chart_type": chart_type,
            "x_column": x_column,
            "y_column": y_column,
            "color_column": color_column,
            "chart_title": chart_title,
            "x_label": x_label,
            "y_label": y_label
        }

        # Create the chart based on user input
        fig = None
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
        if fig:
            st.plotly_chart(fig)

        # Provide option to save the visualization
        with st.form(key='save_visualization_form'):
            chart_name = st.text_input("Save Visualization As", f"{chart_type}_{x_column}_{y_column}")
            save_button = st.form_submit_button("Save Visualization")

        if save_button:
            user_email = st.session_state.get("user_email", "unknown_user@example.com")  # Replace with actual user email retrieval
            save_visualization(client, user_email, chart_name, 
                               st.session_state.chart_details["chart_type"], 
                               st.session_state.chart_details["x_column"], 
                               st.session_state.chart_details["y_column"], 
                               st.session_state.chart_details["color_column"], 
                               st.session_state.chart_details["chart_title"], 
                               st.session_state.chart_details["x_label"], 
                               st.session_state.chart_details["y_label"])

def display_saved_visualizations(client, df):
    st.subheader("Load Saved Visualizations")

    saved_visualizations = load_visualizations(client)
    if not saved_visualizations:
        st.warning("No saved visualizations found.")
        return

    chart_names = [viz['name'] for viz in saved_visualizations]
    selected_chart = st.selectbox("Select Visualization to Load", chart_names)

    if st.button("Load Visualization"):
        selected_viz = next(viz for viz in saved_visualizations if viz['name'] == selected_chart)
        st.write(f"Loading visualization: {selected_chart}")

        fig = None
        if selected_viz['type'] == "Bar":
            fig = px.bar(df, x=selected_viz['x_column'], y=selected_viz['y_column'], color=selected_viz['color_column'], 
                         title=selected_viz['chart_title'], labels={selected_viz['x_column']: selected_viz['x_label'], 
                         selected_viz['y_column']: selected_viz['y_label']})
        elif selected_viz['type'] == "Line":
            fig = px.line(df, x=selected_viz['x_column'], y=selected_viz['y_column'], color=selected_viz['color_column'], 
                          title=selected_viz['chart_title'], labels={selected_viz['x_column']: selected_viz['x_label'], 
                          selected_viz['y_column']: selected_viz['y_label']})
        elif selected_viz['type'] == "Scatter":
            fig = px.scatter(df, x=selected_viz['x_column'], y=selected_viz['y_column'], color=selected_viz['color_column'], 
                             title=selected_viz['chart_title'], labels={selected_viz['x_column']: selected_viz['x_label'], 
                             selected_viz['y_column']: selected_viz['y_label']})
        elif selected_viz['type'] == "Histogram":
            fig = px.histogram(df, x=selected_viz['x_column'], color=selected_viz['color_column'], 
                               title=selected_viz['chart_title'], labels={selected_viz['x_column']: selected_viz['x_label']})
        elif selected_viz['type'] == "Pie":
            fig = px.pie(df, names=selected_viz['x_column'], values=selected_viz['y_column'], 
                         title=selected_viz['chart_title'])

        # Display the chart
        if fig:
            st.plotly_chart(fig)

def display_selected_charts(client, df, page_name):
    st.title(f"{page_name}")

    db = client['netsuite']
    pages_collection = db['pages']

    page_config = pages_collection.find_one({"page_name": page_name})
    if not page_config or not page_config.get("selected_charts"):
        st.warning(f"No charts configured for {page_name}.")
        return

    saved_visualizations = load_visualizations(client)
    selected_charts = page_config['selected_charts']

    for chart_name in selected_charts:
        chart = next((viz for viz in saved_visualizations if viz['name'] == chart_name), None)
        if chart:
            st.subheader(chart['chart_title'])
            fig = None
            if chart['type'] == "Bar":
                fig = px.bar(df, x=chart['x_column'], y=chart['y_column'], color=chart['color_column'], 
                             title=chart['chart_title'], labels={chart['x_column']: chart['x_label'], 
                             chart['y_column']: chart['y_label']})
            elif chart['type'] == "Line":
                fig = px.line(df, x=chart['x_column'], y=chart['y_column'], color=chart['color_column'], 
                              title=chart['chart_title'], labels={chart['x_column']: chart['x_label'], 
                              chart['y_column']: chart['y_label']})
            elif chart['type'] == "Scatter":
                fig = px.scatter(df, x=chart['x_column'], y=chart['y_column'], color=chart['color_column'], 
                                 title=chart['chart_title'], labels={chart['x_column']: chart['x_label'], 
                                 chart['y_column']: chart['y_label']})
            elif chart['type'] == "Histogram":
                fig = px.histogram(df, x=chart['x_column'], color=chart['color_column'], 
                                   title=chart['chart_title'], labels={chart['x_column']: chart['x_label']})
            elif chart['type'] == "Pie":
                fig = px.pie(df, names=chart['x_column'], values=chart['y_column'], title=chart['chart_title'])

            # Display the chart
            if fig:
                st.plotly_chart(fig)

def main():
    st.title("Data Visualization Tool")

    # Connect to MongoDB using the utility function
    client = get_mongo_client()

    # Load the 'salesLines' collection into a DataFrame
    data = get_collection_data(client, 'salesLines')

    # Apply global filters
    filtered_data = apply_global_filters(data)

    # Check if DataFrame is empty after filtering
    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        st.write(f"Number of Rows: {filtered_data.shape[0]}")

        # Create visualizations with preview and save functionality
        create_visualizations(filtered_data, client)

        # Load and display saved visualizations
        display_saved_visualizations(client, filtered_data)

        # Optionally display selected charts from a specific page
        # Uncomment the following line if you have page configurations
        # display_selected_charts(client, filtered_data, "04_Sales")

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
                update_mode="MODEL_CHANGED"
            )

if __name__ == "__main__":
    main()
