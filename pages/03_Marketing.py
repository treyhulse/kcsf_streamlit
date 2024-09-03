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
from datetime import datetime

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

def get_collection_data(client, collection_name):
    db = client['netsuite']
    collection = db[collection_name]
    data = pd.DataFrame(list(collection.find().limit(5)))  # Fetch only the first 5 rows
    if '_id' in data.columns:
        data.drop('_id', axis=1, inplace=True)
    return data

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

    # Step 1: Select the database collection
    client = get_mongo_client()
    collection_names = client['netsuite'].list_collection_names()
    collection_name = st.selectbox("Select a collection", collection_names)

    # Step 2: Display the first 5 rows of the selected collection
    if collection_name:
        data = get_collection_data(client, collection_name)
        st.write(f"First 5 rows of `{collection_name}` collection:")
        st.dataframe(data)

        if not data.empty:
            # Step 3: Provide form to fill out using fields in the collection
            with st.form(key='visualization_form'):
                x_column = st.selectbox("Select X-axis column", data.columns)
                y_column = st.selectbox("Select Y-axis column", data.columns)
                chart_type = st.selectbox("Select chart type", ["Bar", "Line", "Scatter", "Histogram", "Pie"])
                chart_title = st.text_input("Chart Title", "My Chart")
                x_label = st.text_input("X-axis Label", x_column)
                y_label = st.text_input("Y-axis Label", y_column)
                color_column = st.selectbox("Color By (optional)", [None] + list(data.columns), index=0)
                preview_button = st.form_submit_button("Preview Visualization")

            # Step 4: After form submission, render visualization
            if preview_button:
                fig = None
                if chart_type == "Bar":
                    fig = px.bar(data, x=x_column, y=y_column, color=color_column if color_column else None, title=chart_title, labels={x_column: x_label, y_column: y_label})
                elif chart_type == "Line":
                    fig = px.line(data, x=x_column, y=y_column, color=color_column if color_column else None, title=chart_title, labels={x_column: x_label, y_column: y_label})
                elif chart_type == "Scatter":
                    fig = px.scatter(data, x=x_column, y=y_column, color=color_column if color_column else None, title=chart_title, labels={x_column: x_label, y_column: y_label})
                elif chart_type == "Histogram":
                    fig = px.histogram(data, x=x_column, color=color_column if color_column else None, title=chart_title, labels={x_column: x_label})
                elif chart_type == "Pie":
                    fig = px.pie(data, names=x_column, values=y_column, title=chart_title)
                
                if fig:
                    st.plotly_chart(fig)
                    # Step 5: Offer the option to save the visualization
                    with st.form(key='save_form'):
                        chart_name = st.text_input("Save Visualization As", "My_Saved_Chart")
                        save_button = st.form_submit_button("Save Visualization")
                        if save_button:
                            user_email = st.session_state.get("user_email", "unknown_user@example.com")
                            save_visualization(client, user_email, chart_name, chart_type, x_column, y_column, color_column, chart_title, x_label, y_label)

if __name__ == "__main__":
    main()
