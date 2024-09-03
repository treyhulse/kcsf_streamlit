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
from datetime import datetime
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
        st.plotly_chart(fig)

        # Save visualization configuration
        chart_name = st.text_input("Save Visualization As", f"{chart_type}_{x_column}_{y_column}")
        if st.button("Save Visualization"):
            user_email = st.session_state.get("user_email", "unknown_user@example.com")  # Example of how you might retrieve the user's email
            save_visualization(client, user_email, chart_name, chart_type, x_column, y_column, color_column, chart_title, x_label, y_label)

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
            # Add other chart types as needed

            if fig:
                st.plotly_chart(fig)

def main():
    client = get_mongo_client()
    df = get_sales_data(client)  # Load the data
    create_visualizations(df, client)  # Visualization creation and preview
    display_selected_charts(client, df, "04_Sales")  # Display selected charts

if __name__ == "__main__":
    main()
