import streamlit as st
import pandas as pd
from pymongo import MongoClient

# MongoDB connection with increased timeout values
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
    return client

# Function to load inventory data from MongoDB
@st.cache_data
def load_inventory_data():
    client = get_mongo_client()
    db = client['netsuite']
    inventory_collection = db['inventory']
    
    inventory_data = list(inventory_collection.find({}))
    inventory_df = pd.DataFrame(inventory_data)
    
    # Drop the '_id' column and unnecessary columns 'On Hand' and 'Available'
    if '_id' in inventory_df.columns:
        inventory_df.drop(columns=['_id'], inplace=True)
    if 'On Hand' in inventory_df.columns:
        inventory_df.drop(columns=['On Hand'], inplace=True)
    if 'Available' in inventory_df.columns:
        inventory_df.drop(columns=['Available'], inplace=True)
    
    return inventory_df

# Main function to render the Streamlit page with filters
def main():
    st.title("Inventory Data with Filters")

    # Load inventory data
    inventory_df = load_inventory_data()

    if not inventory_df.empty:
        # Create search options for 'Internal ID'
        internal_id_search = st.text_input("Search Internal ID")
        if internal_id_search:
            inventory_df = inventory_df[inventory_df['Internal ID'].str.contains(internal_id_search, case=False, na=False)]

        # Create search options for 'Item'
        item_search = st.text_input("Search Item")
        if item_search:
            inventory_df = inventory_df[inventory_df['Item'].str.contains(item_search, case=False, na=False)]

        # Multi-select for 'Warehouse'
        warehouses = inventory_df['Warehouse'].unique().tolist()
        selected_warehouses = st.multiselect("Select Warehouse", warehouses, default=warehouses)
        if selected_warehouses:
            inventory_df = inventory_df[inventory_df['Warehouse'].isin(selected_warehouses)]

        # Multi-select for 'Cart Flag Field'
        if 'Cart Flag Field' in inventory_df.columns:
            cart_flags = inventory_df['Cart Flag Field'].unique().tolist()
            selected_cart_flags = st.multiselect("Select Cart Flag Field", cart_flags, default=cart_flags)
            if selected_cart_flags:
                inventory_df = inventory_df[inventory_df['Cart Flag Field'].isin(selected_cart_flags)]

        # Multi-select for 'Amazon Flag Field'
        if 'Amazon Flag Field' in inventory_df.columns:
            amazon_flags = inventory_df['Amazon Flag Field'].unique().tolist()
            selected_amazon_flags = st.multiselect("Select Amazon Flag Field", amazon_flags, default=amazon_flags)
            if selected_amazon_flags:
                inventory_df = inventory_df[inventory_df['Amazon Flag Field'].isin(selected_amazon_flags)]

        # Display filtered data
        st.write(f"Showing {len(inventory_df)} records after applying filters.")
        st.dataframe(inventory_df)

if __name__ == "__main__":
    main()
