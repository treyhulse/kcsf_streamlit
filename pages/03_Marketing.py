import logging
import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

@st.cache_data(ttl=600)
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
        for doc in collection.find():
            try:
                # Process each document individually
                processed_doc = {}
                for key, value in doc.items():
                    if isinstance(value, str):
                        processed_doc[key] = value.encode('utf-8', 'ignore').decode('utf-8')
                    else:
                        processed_doc[key] = value
                data.append(processed_doc)
            except Exception as e:
                logging.error(f"Skipping problematic document {doc.get('_id', 'Unknown ID')}: {e}")
                continue  # Skip problematic document
        
        df = pd.DataFrame(data)
        logging.info(f"Data fetched successfully from {collection_name} with shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Error fetching data from collection {collection_name}: {e}")
        raise

def create_visualizations(df):
    st.subheader("Create Your Own Visualizations")

    # Select columns for X and Y axes
    x_column = st.selectbox("Select X-axis column", df.columns)
    y_column = st.selectbox("Select Y-axis column", df.columns)

    # Select the type of chart
    chart_type = st.selectbox("Select chart type", ["Bar", "Line", "Scatter", "Histogram"])

    # Create the chart based on user input
    if chart_type == "Bar":
        fig = px.bar(df, x=x_column, y=y_column)
    elif chart_type == "Line":
        fig = px.line(df, x=x_column, y=y_column)
    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x_column, y=y_column)
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x_column)

    # Display the chart
    st.plotly_chart(fig)

def main():
    st.title("MongoDB Data Visualization Tool")

    # Connect to MongoDB using the utility function
    client = get_mongo_client()

    # Collection selection using buttons
    collection_name = None
    if st.button('Sales'):
        collection_name = 'sales'
    elif st.button('Items'):
        collection_name = 'items'
    elif st.button('Inventory'):
        collection_name = 'inventory'
    elif st.button('Customers'):
        collection_name = 'customers'

    if collection_name:
        # Load the selected collection into a DataFrame
        data = get_collection_data(client, collection_name)

        # Check if DataFrame is empty after loading
        if data.empty:
            st.warning("No data available in the selected collection.")
        else:
            st.write(f"Loaded DataFrame: {data.shape[0]} rows")
            st.dataframe(data)

            # Call the visualization function
            create_visualizations(data)

if __name__ == "__main__":
    main()
