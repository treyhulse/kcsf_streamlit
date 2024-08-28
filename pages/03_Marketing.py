# main_streamlit_page.py (Example file name)

import logging
import streamlit as st
from utils.mongo_connection import get_mongo_client, get_collection_data

# Configure logging for the main page
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

def main():
    try:
        st.title("MongoDB Collections Viewer")

        # Connect to MongoDB using the utility function
        client = get_mongo_client()

        # Select the collection to display
        collection_name = st.selectbox("Choose a collection", ["sales", "items", "inventory", "customers"])

        # Get the data from the chosen collection using the utility function
        data = get_collection_data(client, collection_name)

        # Display the data
        st.write(data)
    except Exception as e:
        logging.critical(f"Critical error in main function: {e}")
        st.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
