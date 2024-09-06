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

import pandas as pd
from pymongo import MongoClient
import utils.shopify_connection as shopify
from bson import Decimal128


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

# Function to post or update products on Shopify
def post_or_update_products():
    st.header("Post or Update Products to Shopify")
    
    # Load the joined items with inventory
    items_df = load_items_with_inventory()
    
    # Debugging: Print the column names to check what fields are available
    st.write("Items DataFrame Columns:", items_df.columns)
    
    if not items_df.empty:
        # Filter the data
        types = items_df['Type'].unique().tolist()
        selected_types = st.multiselect("Select Product Types", types, default=types)
        if selected_types:
            items_df = items_df[items_df['Type'].isin(selected_types)]

        if 'Cart Flag Field' in items_df.columns:
            cart_flags = items_df['Cart Flag Field'].unique().tolist()
            selected_cart_flags = st.multiselect("Select Cart Flag Field", cart_flags, default=cart_flags)
            if selected_cart_flags:
                items_df = items_df[items_df['Cart Flag Field'].isin(selected_cart_flags)]

        if 'Amazon Flag Field' in items_df.columns:
            amazon_flags = items_df['Amazon Flag Field'].unique().tolist()
            selected_amazon_flags = st.multiselect("Select Amazon Flag Field", amazon_flags, default=amazon_flags)
            if selected_amazon_flags:
                items_df = items_df[items_df['Amazon Flag Field'].isin(selected_amazon_flags)]

        # Display filtered data
        st.write(f"Showing {len(items_df)} records after applying filters.")
        st.dataframe(items_df)
        
        if st.button("Post/Update Filtered Products to Shopify"):
            for _, row in items_df.iterrows():
                # Debugging: Print the row to see what fields are available
                st.write("Current Row:", row)
                
                # Check which column represents the SKU
                sku = row['Name']  # Check and confirm 'Name' represents SKU, adjust if necessary
                item_name = row['Name']
                price = row['Price']
                description = f"Product of type {row['Type']}"
                available_inventory = row['Available']

                # Check if SKU exists on Shopify
                if shopify.sku_exists_on_shopify(sku):
                    # Update the existing product
                    update_data = shopify.prepare_update_data(item_name, description, price, available_inventory)
                    response = shopify.update_product_on_shopify(sku, update_data)
                    
                    if response:
                        st.success(f"Updated {item_name} (SKU: {sku}) on Shopify.")
                    else:
                        st.error(f"Failed to update {item_name} (SKU: {sku}) on Shopify.")
                else:
                    # Post new product
                    product_data = shopify.prepare_product_data(item_name, description, price, sku)
                    response = shopify.post_product_to_shopify(product_data)
                    
                    if response:
                        st.success(f"Posted {item_name} (SKU: {sku}) to Shopify.")
                    else:
                        st.error(f"Failed to post {item_name} (SKU: {sku}) to Shopify.")
    else:
        st.warning("No products with available inventory.")



# Function to retrieve synced products from Shopify
def retrieve_synced_products():
    st.header("Synced Products from Shopify")
    
    # Fetch products from Shopify
    products = shopify.get_synced_products_from_shopify()
    
    if products:
        products_df = pd.DataFrame(products)
        st.write(f"Showing {len(products_df)} synced products from Shopify.")
        st.dataframe(products_df)
    else:
        st.warning("No synced products found.")


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
        
        # Check if 'Name' exists in both DataFrames
        if 'Name' in items_df.columns and 'Name' in shopify_df.columns:
            # Merge based on 'Name'
            merged_df = pd.merge(items_df, shopify_df, on='Name', suffixes=('_mongo', '_shopify'))
        elif 'SKU' in items_df.columns and 'SKU' in shopify_df.columns:
            # If 'Name' doesn't exist, try merging on 'SKU'
            merged_df = pd.merge(items_df, shopify_df, on='SKU', suffixes=('_mongo', '_shopify'))
        else:
            st.error("'Name' or 'SKU' is missing from one of the DataFrames.")
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
                else:
                    st.error(f"Failed to sync SKU {sku}.")
    else:
        st.warning("No matching products found or no data available.")

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
