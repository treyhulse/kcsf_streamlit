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

# Function to display and filter inventory data, allowing staging of products
def display_inventory(tab_key=""):
    st.header("Inventory Data with Filters")
    
    # Load inventory data
    inventory_df = load_inventory_data()
    
    if not inventory_df.empty:
        # Create search options for 'Internal ID'
        internal_id_search = st.text_input(f"Search Internal ID {tab_key}", key=f"internal_id_search_{tab_key}")
        if internal_id_search:
            inventory_df = inventory_df[inventory_df['Internal ID'].str.contains(internal_id_search, case=False, na=False)]
    
        # Create search options for 'Item'
        item_search = st.text_input(f"Search Item {tab_key}", key=f"item_search_{tab_key}")
        if item_search:
            inventory_df = inventory_df[inventory_df['Item'].str.contains(item_search, case=False, na=False)]
    
        # Multi-select for 'Warehouse'
        warehouses = inventory_df['Warehouse'].unique().tolist()
        selected_warehouses = st.multiselect(f"Select Warehouse {tab_key}", warehouses, default=warehouses, key=f"warehouse_{tab_key}")
        if selected_warehouses:
            inventory_df = inventory_df[inventory_df['Warehouse'].isin(selected_warehouses)]
    
        # Display filtered data
        st.write(f"Showing {len(inventory_df)} records after applying filters.")
        st.dataframe(inventory_df)
        
        # Staging section - Multi-select to stage products for Shopify
        st.subheader("Stage Products for Shopify")
        staged_products = st.multiselect(f"Select Products to Stage {tab_key}", inventory_df['Item'].unique(), key=f"staged_products_{tab_key}")

        if staged_products:
            # Show the products selected for staging
            st.write(f"Staged Products: {', '.join(staged_products)}")
            
            # Input for additional product details
            description = st.text_area(f"Product Description (optional) {tab_key}", "Enter a description for the selected products", key=f"description_{tab_key}")
            
            if st.button(f"Push to Shopify {tab_key}", key=f"push_to_shopify_{tab_key}"):
                # Loop through the staged products and post them to Shopify
                for product in staged_products:
                    # Get product details from the selected inventory row
                    selected_row = inventory_df[inventory_df['Item'] == product].iloc[0]
                    item_name = selected_row['Item']
                    sku = selected_row['SKU'] if 'SKU' in selected_row else 'default-sku'
                    price = selected_row['Price'] if 'Price' in selected_row else '0.00'
                    
                    # Prepare product data
                    product_data = shopify.prepare_product_data(item_name, description, price, sku)
                    
                    # Post product to Shopify
                    response = shopify.post_product_to_shopify(product_data)
                    
                    if response:
                        st.success(f"Successfully posted {item_name} to Shopify!")
                    else:
                        st.error(f"Failed to post {item_name} to Shopify.")
        else:
            st.warning("No products staged.")


# Function to synchronize inventory and price between MongoDB and Shopify
def sync_inventory_and_price():
    st.header("Sync Inventory and Prices")
    
    # Load inventory data
    inventory_df = load_inventory_data()
    
    # Display inventory data (reduced version)
    st.write(f"Synchronizing {len(inventory_df)} products")
    st.dataframe(inventory_df[['Item', 'Price', 'Quantity']])  # Display key fields
    
    if st.button("Sync Now"):
        for _, row in inventory_df.iterrows():
            # Assume product is already on Shopify, use SKU to find the product
            sku = row['SKU']
            price = row['Price']
            quantity = row['Quantity']  # Add Quantity field to MongoDB if not already present
            
            # Update product price and inventory levels in Shopify using your update API logic
            update_data = {
                "variant": {
                    "price": price,
                    "inventory_quantity": quantity
                }
            }
            
            response = shopify.update_product_inventory_and_price(sku, update_data)
            
            if response:
                st.success(f"Updated {row['Item']} successfully")
            else:
                st.error(f"Failed to update {row['Item']}")

# Main function to render the Streamlit page
def main():
    st.title("API Portal - Product Staging & Shopify Integration")
    
    # Tabs for navigation
    tab1, tab2, tab3, tab4 = st.tabs(["Home", "Stage Products", "View Inventory", "Sync Inventory/Prices"])
    
    with tab1:
        st.markdown("""
            ## Welcome to the API Portal
            Use the tabs to navigate between different functionalities:
            - **Stage Products**: Stage selected products for posting to Shopify.
            - **View Inventory**: View and filter your inventory data.
            - **Sync Inventory/Prices**: Keep inventory and price levels current with Shopify.
        """)
        
    with tab2:
        display_inventory(tab_key="stage_products")

    with tab3:
        display_inventory(tab_key="view_inventory")

    with tab4:
        sync_inventory_and_price()

if __name__ == "__main__":
    main()

