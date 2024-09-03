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
        logging.debug("Attempting to connect to MongoDB...")
        connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
        client = MongoClient(connection_string, 
                             ssl=True,
                             serverSelectionTimeoutMS=60000,  # Increase server selection timeout
                             connectTimeoutMS=60000,          # Increase connection timeout
                             socketTimeoutMS=60000)           # Increase socket timeout
        logging.info("MongoDB connection successful")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise

def get_collection_data(client, collection_name):
    try:
        logging.debug(f"Fetching data from collection: {collection_name}")
        db = client['netsuite']
        collection = db[collection_name]

        data = []
        cursor = collection.find()
        
        for doc in cursor:
            data.append(doc)
        
        df = pd.DataFrame(data)
        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)
        
        return df
    except pymongo.errors.NetworkTimeout as e:
        st.error("Network timeout occurred while fetching data. Please try again later.")
        logging.error(f"Network timeout error: {e}")
        return pd.DataFrame()  # Return an empty DataFrame as a fallback
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame as a fallback

def create_visualizations(df):
    st.subheader("Create and Preview Your Visualization")

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
        if fig:
            st.plotly_chart(fig)

        # Provide option to save the visualization
        with st.form(key='save_visualization_form'):
            st.write("If you like this visualization, you can save it.")
            chart_name = st.text_input("Save Visualization As", f"{chart_type}_{x_column}_{y_column}")
            save_button = st.form_submit_button("Save Visualization")

        if save_button:
            client = get_mongo_client()  # Get MongoDB client
            user_email = st.session_state.get("user_email", "unknown_user@example.com")  # Replace with actual user email retrieval
            save_visualization(client, user_email, chart_name, chart_type, x_column, y_column, color_column, chart_title, x_label, y_label)
            st.success(f"Visualization '{chart_name}' saved successfully.")

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

def main():
    st.title("Data Visualization Tool")

    # Connect to MongoDB using the utility function
    client = get_mongo_client()

    # Load the 'salesLines' collection into a DataFrame
    data = get_collection_data(client, 'salesLines')

    # Create visualizations with preview and save functionality
    create_visualizations(data)

if __name__ == "__main__":
    main()
