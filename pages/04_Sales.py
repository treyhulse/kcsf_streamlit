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

def load_visualizations(client):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        
        return list(charts_collection.find())
    except Exception as e:
        st.error(f"Failed to load visualizations: {e}")
        logging.error(f"Failed to load visualizations: {e}")
        return []

def display_selected_charts(client, page_name):
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
    display_selected_charts(client, "04_Sales")

if __name__ == "__main__":
    main()
