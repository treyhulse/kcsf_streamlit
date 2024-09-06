import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'API Portal'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

from bson import Decimal128
import streamlit as st
import pandas as pd
import utils.shopify_connection as shopify

# MongoDB connection with increased timeout values
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(
        connection_string,
        ssl=True,
        serverSelectionTimeoutMS=60000,
        connectTimeoutMS=60000,
        socketTimeoutMS=60000
    )
    return client

# Function to load 'items' collection and join it with the 'Available' inventory data using 'Internal ID'
@st.cache_data
def load_items_with_inventory():
    client = get_mongo_client()
    db = client['netsuite']
    items_collection = db['items']
    inventory_collection = db['inventory']
    
    # Load 'items' collection
    items_data = list(items_collection.find({}))
    items_df = pd.DataFrame(items_data)
    
    # Load 'inventory' collection
    inventory_data = list(inventory_collection.find({}))
    
    # Check if inventory data is empty
    if len(inventory_data) == 0:
        st.error("Inventory data is empty. Please check your MongoDB 'inventory' collection.")
        return pd.DataFrame()  # Return an empty DataFrame if no inventory data

    # Convert inventory data to DataFrame
    inventory_df = pd.DataFrame(inventory_data)

    # Ensure 'Internal ID' is present in both DataFrames and is a string
    if 'Internal ID' in items_df.columns and 'Internal ID' in inventory_df.columns:
        # Convert 'Internal ID' to string in both DataFrames
        items_df['Internal ID'] = items_df['Internal ID'].astype(str)
        inventory_df['Internal ID'] = inventory_df['Internal ID'].astype(str)
        
        # Perform the merge
        merged_df = pd.merge(items_df, inventory_df[['Internal ID', 'Available']], on='Internal ID')
    else:
        st.error("'Internal ID' is missing from one of the DataFrames.")
        return pd.DataFrame()  # Return an empty DataFrame if the join can't be performed

    # Convert 'Available' column from Decimal128 to float
    def decimal128_to_float(value):
        if isinstance(value, Decimal128):
            return float(value.to_decimal())
        else:
            return float(value)
    
    # Apply the conversion function to the 'Available' column
    merged_df['Available'] = merged_df['Available'].apply(decimal128_to_float)

    # Filter out rows where 'Available' is 0 or NaN
    merged_df = merged_df[merged_df['Available'] > 0]

    # Drop unnecessary '_id' column
    if '_id' in merged_df.columns:
        merged_df.drop(columns=['_id'], inplace=True)
    
    return merged_df

# Function to match items between MongoDB and Shopify platforms
def match_items_between_platforms():
    st.header("Match Items for Pricing and Inventory Management")
    
    # Load 'items' from MongoDB and synced products from Shopify
    items_df = load_items_with_inventory()
    shopify_products = shopify.get_synced_products_from_shopify()
    
    if not items_df.empty and shopify_products:
        shopify_df = pd.DataFrame(shopify_products)
        
        # Debugging: Print the columns from both DataFrames
        st.write("Items DataFrame Columns:", items_df.columns)
        st.write("Shopify DataFrame Columns:", shopify_df.columns)
        
        # Check if 'Item' exists in both DataFrames
        if 'Item' in items_df.columns and 'Item' in shopify_df.columns:
            # Merge based on 'Item'
            merged_df = pd.merge(items_df, shopify_df, on='Item', suffixes=('_mongo', '_shopify'))
        elif 'SKU' in items_df.columns and 'SKU' in shopify_df.columns:
            # If 'Item' doesn't exist, try merging on 'SKU'
            merged_df = pd.merge(items_df, shopify_df, on='SKU', suffixes=('_mongo', '_shopify'))
        else:
            st.error("'Item' or 'SKU' is missing from one of the DataFrames.")
            return
        
        # Display comparison of pricing and inventory
        st.write("Matched Products Between MongoDB and Shopify:")
        st.dataframe(merged_df[['SKU', 'Price_mongo', 'Price_shopify', 'Available_mongo', 'Available_shopify']])
        
        if st.button("Sync Inventory and Pricing"):
            for _, row in merged_df.iterrows():
                # Update Shopify product with MongoDB data
                sku = row['SKU']
                new_price = row['Price_mongo']
                new_inventory = row['Available_mongo']
                
                update_data = {
                    "variant": {
                        "price": new_price,
                        "inventory_quantity": new_inventory
                    }
                }
                
                response = shopify.update_product_on_shopify(sku, update_data)
                
                if response:
                    st.success(f"Synced SKU {sku} with new price and inventory.")
                    logger.info(f"Synced SKU {sku} with new price and inventory.")
                else:
                    st.error(f"Failed to sync SKU {sku}.")
                    logger.error(f"Failed to sync SKU {sku}.")
    else:
        st.warning("No matching products found or no data available.")
        logger.warning("No matching products found between MongoDB and Shopify.")

# Main function to render the Streamlit page
def main():
    st.title("API Portal - Shopify Integration")
    
    # Tabs for navigation
    tab1, tab2, tab3 = st.tabs(["Post/Update Products", "Retrieve Synced Products", "Manage Pricing/Inventory"])
    
    with tab1:
        post_or_update_products()

    with tab2:
        retrieve_synced_products()

    with tab3:
        match_items_between_platforms()

if __name__ == "__main__":
    main()
