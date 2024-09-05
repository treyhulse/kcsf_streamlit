import streamlit as st
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

# Function to authenticate Shopify and ensure connection is valid
def authenticate_shopify():
    st.header("Shopify Connection")
    if st.button("Test Shopify Connection"):
        shop_info = shopify.test_shopify_connection()
        if shop_info:
            st.subheader("Shop Information")
            st.json(shop_info)
        else:
            st.error("Shopify connection failed. Please check your credentials.")

# Function to display and filter inventory data
def display_inventory():
    st.header("Inventory Data with Filters")
    
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
        
        # Allow users to select an item to post to Shopify
        st.subheader("Post Product to Shopify")
        selected_item = st.selectbox("Select Item to Post", inventory_df['Item'].unique())
        
        if selected_item:
            selected_row = inventory_df[inventory_df['Item'] == selected_item].iloc[0]
            item_name = selected_row['Item']
            sku = selected_row['SKU'] if 'SKU' in selected_row else 'default-sku'
            price = selected_row['Price'] if 'Price' in selected_row else '0.00'
            
            # Input for additional product details (optional)
            description = st.text_area("Product Description", "Enter product description here")
            
            # Button to post to Shopify
            if st.button("Post to Shopify"):
                # Prepare product data
                product_data = shopify.prepare_product_data(item_name, description, price, sku)
                
                # Post product to Shopify
                response = shopify.post_product_to_shopify(product_data)
                
                if response:
                    st.success("Product successfully posted to Shopify!")
                    st.json(response)
                else:
                    st.error("Failed to post product to Shopify.")
    else:
        st.warning("No inventory data available.")

# Main function to render the Streamlit page
def main():
    st.title("API Portal - Inventory & Shopify Integration")
    
    # Tabs for navigation
    tab1, tab2, tab3 = st.tabs(["Home", "Test Shopify Connection", "View Inventory"])
    
    with tab1:
        st.markdown("""
            ## Welcome to the API Portal
            Use the tabs to navigate between different functionalities:
            - **Test Shopify Connection**: Verify your Shopify API credentials.
            - **View Inventory**: View and manage your inventory data, and post products to Shopify.
        """)
        
    with tab2:
        authenticate_shopify()

    with tab3:
        display_inventory()

if __name__ == "__main__":
    main()
