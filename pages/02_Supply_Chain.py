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


import logging
from pymongo import MongoClient
import pandas as pd

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

# Function to retrieve data with pagination from MongoDB
def get_collection_data_with_progress(client, collection_name, progress_bar, batch_size=100):
    db = client['netsuite']
    collection = db[collection_name]
    
    data = []
    total_docs = collection.estimated_document_count()
    
    for i, doc in enumerate(collection.find().batch_size(batch_size)):
        processed_doc = {key: value for key, value in doc.items()}
        data.append(processed_doc)
        
        # Update progress bar
        progress = (i + 1) / total_docs
        progress_bar.progress(progress)
    
    df = pd.DataFrame(data)
    
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    
    logging.info(f"Data fetched successfully from {collection_name} with shape: {df.shape}")
    return df

# Main function
def main():
    st.title("Supply Chain Data Viewer")
    
    # Connect to MongoDB using the utility function
    client = MongoClient(st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority", 
                         ssl=True, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000, socketTimeoutMS=30000)

    # Select the collection to view
    collection_name = st.selectbox("Choose a collection to load", ["items", "inventory"])

    # Display a progress bar
    progress_bar = st.progress(0)

    # Load the selected collection into a DataFrame
    with st.spinner(f"Loading {collection_name} data..."):
        data = get_collection_data_with_progress(client, collection_name, progress_bar, batch_size=100)

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
