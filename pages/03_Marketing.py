import pymongo
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
import streamlit as st
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

@st.cache_resource
def get_mongo_client():
    try:
        connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
        client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
        logging.info("MongoDB connection successful")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise

def get_collection_data(client):
    db = client['netsuite']
    collection = db['salesLines']
    data = pd.DataFrame(list(collection.find()))
    if '_id' in data.columns:
        data.drop('_id', axis=1, inplace=True)
    return data

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

    # Filter by Date
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        date_filter = st.sidebar.selectbox(
            "Filter by Date", 
            ["This Month", "Today", "Tomorrow", "This Week", "Last Week", "Last Month", 
             "First Quarter", "Second Quarter", "Third Quarter", "Fourth Quarter", "Next Month", "Custom"],
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
            next_month = start_date.replace(day=28) + timedelta(days=4)
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

        if 'start_date' in locals() and 'end_date' in locals():
            df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    return df

def save_visualization(client, user_email, chart_name, chart_type, x_column, y_column, color_column, chart_title, x_label, y_label):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        chart_data = {
            "name": chart_name,
            "user": user_email,
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
        st.success(f"Visualization '{chart_name}' saved successfully.")
    except Exception as e:
        st.error(f"Failed to save visualization: {e}")
        logging.error(f"Failed to save visualization: {e}")

def main():
    st.title("Data Visualization Tool")

    client = get_mongo_client()

    # Load the 'salesLines' collection into a DataFrame and apply filters
    data = get_collection_data(client)
    filtered_data = apply_global_filters(data)

    # Show the first 5 rows of the filtered data
    st.write(f"First 5 rows of the filtered `salesLines` collection:")
    st.dataframe(filtered_data.head(5))

    # Proceed if there is data after filtering
    if not filtered_data.empty:
        with st.form(key='visualization_form'):
            x_column = st.selectbox("Select X-axis column", filtered_data.columns)
            y_column = st.selectbox("Select Y-axis column", filtered_data.columns)
            chart_type = st.selectbox("Select chart type", ["Bar", "Line", "Scatter", "Histogram", "Pie"])
            chart_title = st.text_input("Chart Title", "My Chart")
            x_label = st.text_input("X-axis Label", x_column)
            y_label = st.text_input("Y-axis Label", y_column)
            color_column = st.selectbox("Color By (optional)", [None] + list(filtered_data.columns), index=0)
            preview_button = st.form_submit_button("Preview Visualization")

        if preview_button:
            fig = None
            if chart_type == "Bar":
                fig = px.bar(filtered_data, x=x_column, y=y_column, color=color_column if color_column else None, title=chart_title, labels={x_column: x_label, y_column: y_label})
            elif chart_type == "Line":
                fig = px.line(filtered_data, x=x_column, y=y_column, color=color_column if color_column else None, title=chart_title, labels={x_column: x_label, y_column: y_label})
            elif chart_type == "Scatter":
                fig = px.scatter(filtered_data, x=x_column, y=y_column, color=color_column if color_column else None, title=chart_title, labels={x_column: x_label, y_column: y_label})
            elif chart_type == "Histogram":
                fig = px.histogram(filtered_data, x=x_column, color=color_column if color_column else None, title=chart_title, labels={x_column: x_label})
            elif chart_type == "Pie":
                fig = px.pie(filtered_data, names=x_column, values=y_column, title=chart_title)
            
            if fig:
                st.plotly_chart(fig)

                with st.form(key='save_form'):
                    chart_name = st.text_input("Save Visualization As", "My_Saved_Chart")
                    save_button = st.form_submit_button("Save Visualization")
                    if save_button:
                        user_email = st.session_state.get("user_email", "unknown_user@example.com")
                        save_visualization(client, user_email, chart_name, chart_type, x_column, y_column, color_column, chart_title, x_label, y_label)

if __name__ == "__main__":
    main()
