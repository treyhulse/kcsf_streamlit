import logging
import streamlit as st
from pymongo import MongoClient
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

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

def get_collection_data(client, collection_name):
    try:
        logging.debug(f"Fetching data from collection: {collection_name}")
        db = client['netsuite']  # Ensure the database name is correct
        collection = db[collection_name]
        
        # Fetch all data and handle encoding errors
        data = list(collection.find())
        
        # Convert each document to string, handling encoding errors
        processed_data = []
        for doc in data:
            processed_doc = {}
            for key, value in doc.items():
                if isinstance(value, str):
                    processed_doc[key] = value.encode('utf-8', 'ignore').decode('utf-8')
                else:
                    processed_doc[key] = value
            processed_data.append(processed_doc)
        
        df = pd.DataFrame(processed_data)
        
        logging.info(f"Data fetched successfully from {collection_name} with shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Error fetching data from collection {collection_name}: {e}")
        raise

def main():
    try:
        st.title("MongoDB Sales Collection Viewer")

        # Connect to MongoDB using the utility function
        client = get_mongo_client()

        # Specify the collection to display (in this case, always 'sales')
        collection_name = "sales"

        # Load the entire collection into a DataFrame
        data = get_collection_data(client, collection_name)

        # Display the data with AgGrid for filtering and sorting
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(filterable=True, sortable=True)
        gb.configure_pagination(enabled=True, paginationAutoPageSize=True)  # Enable pagination if needed
        grid_options = gb.build()

        AgGrid(data, gridOptions=grid_options)
    except Exception as e:
        logging.critical(f"Critical error in main function: {e}")
        st.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
