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
import requests
from utils.apis import get_shopify_products, post_product_to_shopify, update_inventory_and_price
from requests_oauthlib import OAuth1
from utils.suiteql import fetch_suiteql_data, fetch_netsuite_inventory

# Helper function to authenticate with NetSuite
def get_authentication():
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_inventory_data():
    url = f"{st.secrets['url_restlet']}?script=inventory_balance"
    auth = get_authentication()

    # Fetch data from NetSuite RESTlet
    try:
        response = requests.get(url, auth=auth, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)  # Convert JSON to DataFrame
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching inventory data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure

st.title("NetSuite & Shopify Product Sync")

# Fetch NetSuite product data from the custom RESTlet
inventory_data = fetch_inventory_data()

# Create the 4 tabs
tabs = st.tabs([
    "View NetSuite Products", 
    "View Shopify Products", 
    "Post Products to Shopify", 
    "Sync Inventory & Price"
])

# Tab 1: View NetSuite Products
with tabs[0]:
    st.subheader("NetSuite Products Marked for Shopify")

    # Display the products from the saved search customsearch0413 (inventory balance)
    if not inventory_data.empty:
        st.dataframe(inventory_data)
    else:
        st.error("No products available from NetSuite.")

# Tab 2: View Shopify Products
with tabs[1]:
    st.subheader("Shopify Products")

    # Fetch Shopify products
    shopify_products = pd.DataFrame(get_shopify_products())

    if not shopify_products.empty:
        st.dataframe(shopify_products)
    else:
        st.error("No products available from Shopify.")

# Tab 3: Inventory & Shopify SKU Match
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
    
    # Merge inventory and Shopify data on SKU/itemid
    matched_data = pd.merge(
        netsuite_inventory, shopify_products, 
        left_on='item_name', right_on='sku', 
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

# Tab 3: Match NetSuite and Shopify inventory
with tabs[2]:
    st.subheader("Match NetSuite Inventory with Shopify Products by SKU")
    match_netsuite_shopify()

# Tab 4: Sync Inventory & Price
with tabs[3]:
    st.subheader("Sync Inventory & Price between NetSuite and Shopify")

    if not shopify_products.empty:
        selected_shopify_product = st.selectbox("Select Shopify Product to Update", shopify_products['title'])

        # Input fields for new price and inventory quantity
        new_price = st.number_input("New Price", min_value=0.0)
        new_inventory = st.number_input("New Inventory Quantity", min_value=0)

        if st.button("Update Product"):
            # Get the product ID from Shopify
            product_id = shopify_products.loc[shopify_products['title'] == selected_shopify_product, 'id'].values[0]

            # Update inventory and price
            status_code, response = update_inventory_and_price(product_id, new_inventory, new_price)

            if status_code == 200:
                st.success("Product updated successfully!")
            else:
                st.error(f"Failed to update product. Response: {response}")
    else:
        st.error("No Shopify products available for update.")
