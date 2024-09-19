import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Order Management'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
from utils.suiteql import fetch_netsuite_inventory
from utils.apis import get_shopify_products

st.title("NetSuite & Shopify Product Sync")

# Helper function to match NetSuite inventory and Shopify products by item_id and SKU
def match_netsuite_shopify():
    # Fetch inventory data from NetSuite (SuiteQL)
    netsuite_inventory = fetch_netsuite_inventory()
    
    # Fetch product data from Shopify
    shopify_products = pd.DataFrame(get_shopify_products())
    
    if netsuite_inventory.empty:
        st.error("No inventory data available from NetSuite.")
        return
    
    if shopify_products.empty:
        st.error("No products available from Shopify.")
        return
    
    # Merge inventory and Shopify data on item_id (NetSuite) and sku (Shopify)
    matched_data = pd.merge(
        netsuite_inventory, shopify_products, 
        left_on='item_id', right_on='sku', 
        how='inner'
    )
    
    if not matched_data.empty:
        st.write(f"Matched {len(matched_data)} products between NetSuite and Shopify.")
        st.dataframe(matched_data)
    else:
        st.error("No matches found between NetSuite and Shopify products based on SKU.")
    

# Create the 4 tabs
tabs = st.tabs([
    "View NetSuite Products", 
    "View Shopify Products", 
    "Post Products to Shopify", 
    "Inventory & Shopify SKU Match"
])

# Tab 1: View NetSuite Products (Example, you can modify as needed)
with tabs[0]:
    st.subheader("NetSuite Products Marked for Shopify")
    netsuite_inventory = fetch_netsuite_inventory()
    if not netsuite_inventory.empty:
        st.dataframe(netsuite_inventory)
    else:
        st.error("No NetSuite products available.")

# Tab 2: View Shopify Products (Example, you can modify as needed)
with tabs[1]:
    st.subheader("Shopify Products")
    shopify_products = pd.DataFrame(get_shopify_products())
    if not shopify_products.empty:
        st.dataframe(shopify_products)
    else:
        st.error("No products available from Shopify.")

# Tab 3: Post Products to Shopify (Example, you can modify as needed)
with tabs[2]:
    st.subheader("Post Products from NetSuite to Shopify")
    if not netsuite_inventory.empty:
        selected_product = st.selectbox("Select Product to Post", netsuite_inventory['item_name'])
        if st.button("Post to Shopify"):
            # Logic for posting to Shopify would go here
            st.success(f"Product {selected_product} posted to Shopify.")
    else:
        st.error("No products available from NetSuite to post.")

# Tab 4: Match NetSuite and Shopify inventory
with tabs[3]:
    st.subheader("Match NetSuite Inventory with Shopify Products by SKU")
    match_netsuite_shopify()
