import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Supply Chain'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
from pymongo import MongoClient

# MongoDB connection with increased timeout values
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
    return client

# Function to load items collection from MongoDB
@st.cache_data
def load_items_data():
    client = get_mongo_client()
    db = client['netsuite']
    items_collection = db['items']
    
    items_data = list(items_collection.find({}))
    items_df = pd.DataFrame(items_data)
    
    # Drop the '_id' column if it exists
    if '_id' in items_df.columns:
        items_df.drop(columns=['_id'], inplace=True)
    
    return items_df

# Function to load inventory collection from MongoDB
@st.cache_data
def load_inventory_data():
    client = get_mongo_client()
    db = client['netsuite']
    inventory_collection = db['inventory']
    
    inventory_data = list(inventory_collection.find({}))
    inventory_df = pd.DataFrame(inventory_data)
    
    # Drop the '_id' column if it exists
    if '_id' in inventory_df.columns:
        inventory_df.drop(columns=['_id'], inplace=True)
    
    return inventory_df

# Function to merge the two dataframes on 'Internal ID'
def merge_dataframes(items_df, inventory_df):
    merged_df = pd.merge(items_df, inventory_df, on="Internal ID", how="inner")
    return merged_df

# Main function to render the Streamlit page
def main():
    st.title("Items and Inventory Merger")

    # Load data from MongoDB collections
    items_df = load_items_data()
    inventory_df = load_inventory_data()

    if not items_df.empty and not inventory_df.empty:
        # Merge the dataframes on 'Internal ID'
        merged_df = merge_dataframes(items_df, inventory_df)

        st.write(f"Merged DataFrame with {len(merged_df)} records:")
        
        # Display the merged dataframe
        st.dataframe(merged_df)

if __name__ == "__main__":
    main()
