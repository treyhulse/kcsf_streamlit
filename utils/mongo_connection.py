import logging
from pymongo import MongoClient
import pandas as pd
import streamlit as st

# Configure logging for the utility file
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

# Modified function to get collection data from MongoDB and handle `_id` correctly
def get_collection_data(client, collection_name):
    try:
        logging.debug(f"Fetching data from collection: {collection_name}")
        db = client['netsuite']  # Ensure the database name is correct
        collection = db[collection_name]

        # Fetch the entire collection and convert it to a DataFrame
        data = pd.DataFrame(list(collection.find()))

        # Convert the '_id' field to a string
        if '_id' in data.columns:
            data['_id'] = data['_id'].apply(str)

        # Print data for debugging
        print(data.head())

        logging.info(f"Data fetched successfully from {collection_name}")
        return data
    except Exception as e:
        logging.error(f"Error fetching data from collection {collection_name}: {e}")
        raise