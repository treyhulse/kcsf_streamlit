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
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

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
    inventory_df = pd.DataFrame(inventory_data)
    
    # Debugging: Print the column names of both DataFrames
    st.write("Items DataFrame Columns:", items_df.columns)
    st.write("Inventory DataFrame Columns:", inventory_df.columns)

    # Perform join on 'Internal ID'
    if 'Internal ID' in items_df.columns and 'Internal ID' in inventory_df.columns:
        merged_df = pd.merge(items_df, inventory_df[['Internal ID', 'Available']], on='Internal ID')
    else:
        st.error("'Internal ID' is missing from one of the DataFrames.")
        return pd.DataFrame()  # Return an empty DataFrame if the join can't be performed

    # Convert 'Available' column from Decimal128 to float
    def decimal128_to_float(value):
        if isinstance(value, pd.api.extensions.ExtensionArray):
            return float(value.to_decimal())
        elif isinstance(value, Decimal128):  # Correctly check for Decimal128 type
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




# Function to post or update items on Shopify
def post_or_update_products():
    st.header("Post or Update Products to Shopify")
    
    # Load the joined items with inventory
    items_df = load_items_with_inventory()
    
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
                sku = row['Item']
                item_name = row['Item']
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
                        logger.info(f"Updated product {item_name} with SKU {sku}.")
                    else:
                        st.error(f"Failed to update {item_name} (SKU: {sku}) on Shopify.")
                else:
                    # Post new product
                    product_data = shopify.prepare_product_data(item_name, description, price, sku)
                    response = shopify.post_product_to_shopify(product_data)
                    
                    if response:
                        st.success(f"Posted {item_name} (SKU: {sku}) to Shopify.")
                        logger.info(f"Posted new product {item_name} with SKU {sku}.")
                    else:
                        st.error(f"Failed to post {item_name} (SKU: {sku}) to Shopify.")
    else:
        st.warning("No products with available inventory.")

# Tab 2: Retrieve synced products from Shopify
def retrieve_synced_products():
    st.header("Synced Products from Shopify")
    
    # Fetch products from Shopify
    products = shopify.get_synced_products_from_shopify()
    
    if products:
        products_df = pd.DataFrame(products)
        st.write(f"Showing {len(products_df)} synced products from Shopify.")
        st.dataframe(products_df)
        logger.info("Fetched synced products from Shopify.")
    else:
        st.warning("No synced products found.")
        logger.warning("No synced products found.")

# Tab 3: Match items between platforms for pricing and inventory management
def match_items_between_platforms():
    st.header("Match Items for Pricing and Inventory Management")
    
    # Load 'items' from MongoDB and synced products from Shopify
    items_df = load_items_with_inventory()
    shopify_products = shopify.get_synced_products_from_shopify()
    
    if not items_df.empty and shopify_products:
        shopify_df = pd.DataFrame(shopify_products)
        
        # Join items_df with shopify_df based on SKU
        merged_df = pd.merge(items_df, shopify_df, on='Item', suffixes=('_mongo', '_shopify'))
        
        # Display comparison of pricing and inventory
        st.write("Matched Products Between MongoDB and Shopify:")
        st.dataframe(merged_df[['Item', 'Price_mongo', 'Price_shopify', 'Available_mongo', 'Available_shopify']])
        
        if st.button("Sync Inventory and Pricing"):
            for _, row in merged_df.iterrows():
                # Update Shopify product with MongoDB data
                sku = row['Item']
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
