import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '05_Shop.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import logging
from pymongo import MongoClient
import streamlit as st

# Configure logging
logging.basicConfig(
    filename="netsuite_page.log", 
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

# Function to fetch and process data from MongoDB
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
                # Process each document into a dictionary
                obj = {
                    "Internal ID": doc.get("Internal ID"),
                    "WO #": doc.get("WO #"),
                    "Item": doc.get("Item"),
                    "Description": doc.get("Description (Display Name)"),
                    "Qty": doc.get("Qty"),
                    "Name": doc.get("Name"),
                    "SO#": doc.get("SO#"),
                    "BO": doc.get("BO"),
                    "WO Status": doc.get("WO Status"),
                    "Sub Status": doc.get("Sub Status"),
                    "Start Date": doc.get("Start Date"),
                    "Completion Date": doc.get("Completion Date"),
                    "Ship Via": doc.get("Ship Via"),
                    "*Here?": doc.get("*Here?")
                }
                data.append(obj)
                
                # Update the progress bar
                progress_bar.progress((i + 1) / total_docs)
                
            except Exception as e:
                logging.error(f"Skipping problematic document {doc.get('_id', 'Unknown ID')}: {e}")
                continue  # Skip problematic document
        
        logging.info(f"Data fetched successfully from {collection_name} with {len(data)} records.")
        return data
    except Exception as e:
        logging.error(f"Error fetching data from collection {collection_name}: {e}")
        raise

def display_objects(data):
    st.write("### Work Order Objects")
    for obj in data:
        st.json(obj)

# Streamlit page layout
def main():
    st.title("NetSuite MongoDB Data Objects")
    
    client = get_mongo_client()
    
    collection_name = st.text_input("Enter MongoDB Collection Name:", "work_orders")
    
    if st.button("Fetch and Display Data"):
        data = get_collection_data(client, collection_name)
        display_objects(data)

if __name__ == "__main__":
    main()
