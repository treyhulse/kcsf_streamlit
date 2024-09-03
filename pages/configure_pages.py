import logging
from pymongo import MongoClient
import streamlit as st

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levellevel)s - %(message)s", 
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

def configure_page_charts(client, page_name):
    st.subheader(f"Configure Charts for {page_name}")

    saved_visualizations = load_visualizations(client)
    if not saved_visualizations:
        st.warning("No saved visualizations found.")
        return

    selected_charts = st.multiselect(
        f"Select charts to display on {page_name}",
        options=[viz['name'] for viz in saved_visualizations],
        default=[]
    )

    if st.button(f"Save Configuration for {page_name}"):
        db = client['netsuite']
        pages_collection = db['pages']

        pages_collection.update_one(
            {"page_name": page_name},
            {"$set": {"selected_charts": selected_charts}},
            upsert=True
        )
        st.success(f"Configuration for {page_name} saved successfully.")

def main():
    client = get_mongo_client()

    st.title("Configure Page Charts")
    configure_page_charts(client, "04_Sales")
    configure_page_charts(client, "08_Showcase")

if __name__ == "__main__":
    main()
