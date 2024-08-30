import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '02_Supply_Chain.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################


# Page title and description
st.title("Supply Chain Insights")
st.write("""
Welcome to the Supply Chain Insights page. Here, you'll find valuable data and metrics to help you manage and optimize 
your supply chain operations, from inventory management to demand forecasting.
""")

# Sidebar configuration
st.sidebar.header("Supply Chain Options")
st.sidebar.write("Use the options below to navigate through supply chain data and analytics.")

# Add any initial content or widgets here
st.subheader("Overview")
st.write("Select options from the sidebar to dive deeper into specific areas of your supply chain.")

import logging
from pymongo import MongoClient
import pandas as pd
import time

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

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

def get_collection_data_with_progress(client, collection_name, progress_bar):
    try:
        logging.debug(f"Fetching data from collection: {collection_name}")
        db = client['netsuite']  # Ensure the database name is correct
        collection = db[collection_name]
        
        data = []
        total_docs = collection.count_documents({})  # Get the total number of documents
        progress = 0

        for i, doc in enumerate(collection.find()):
            try:
                processed_doc = {}
                for key, value in doc.items():
                    if isinstance(value, str):
                        processed_doc[key] = value.encode('utf-8', 'ignore').decode('utf-8')
                    else:
                        processed_doc[key] = value
                data.append(processed_doc)

                # Update the progress bar
                progress = (i + 1) / total_docs
                progress_bar.progress(progress)
            except Exception as e:
                logging.error(f"Skipping problematic document {doc.get('_id', 'Unknown ID')}: {e}")
                continue
        
        df = pd.DataFrame(data)

        # Remove the '_id' column if it exists
        if '_id' in df.columns:
            df.drop(columns=['_id'], inplace=True)

        logging.info(f"Data fetched successfully from {collection_name} with shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Error fetching data from collection {collection_name}: {e}")
        raise

def main():
    st.title("Items and Inventory Data Viewer")

    # Connect to MongoDB using the utility function
    client = get_mongo_client()

    # Select the collection to view
    collection_name = st.selectbox("Choose a collection to load", ["items", "inventory"])

    # Display a progress bar
    progress_bar = st.progress(0)

    # Load the selected collection into a DataFrame
    with st.spinner(f"Loading {collection_name} data..."):
        data = get_collection_data_with_progress(client, collection_name, progress_bar)

    # Check if DataFrame is empty
    if data.empty:
        st.warning(f"No data available in the {collection_name} collection.")
    else:
        st.write(f"{collection_name.capitalize()} DataFrame: {data.shape[0]} rows")
        st.dataframe(data)

    # Complete the progress bar
    progress_bar.progress(100)

if __name__ == "__main__":
    main()
