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
from utils.restlet import fetch_restlet_data  # Pulls data from RESTlet for customsearch
from utils.suiteql import fetch_netsuite_inventory  # For SuiteQL inventory sync
from utils.apis import get_shopify_products

st.title("NetSuite & Shopify Product Sync")

# Fetch data from customsearch5131 using the RESTlet method
@st.cache_data(ttl=900)
def fetch_customsearch5131_data():
    return fetch_restlet_data("customsearch5131")  # Using the saved search ID

# Helper function to match NetSuite inventory and Shopify products by name/title
def match_netsuite_shopify_by_title():
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
    
    # Merge inventory and Shopify data on Title (NetSuite) and title (Shopify)
    matched_data = pd.merge(
        netsuite_inventory, shopify_products, 
        left_on='Title', right_on='title', 
        how='inner'
    )
    
    if not matched_data.empty:
        st.write(f"Matched {len(matched_data)} products between NetSuite and Shopify by title.")
        st.dataframe(matched_data)
    else:
        st.error("No matches found between NetSuite and Shopify products based on title.")

# Create the 4 tabs
tabs = st.tabs([
    "View NetSuite Products (Custom Search 5131)", 
    "View Shopify Products", 
    "Inventory Sync (SuiteQL)", 
    "Post Products to Shopify"
])

# Tab 1: View NetSuite Products (Custom Search 5131)
with tabs[0]:
    st.subheader("NetSuite Products - Custom Search 5131")
    
    # Fetch and display the customsearch5131 data
    customsearch5131_data = fetch_customsearch5131_data()
    
    if not customsearch5131_data.empty:
        st.dataframe(customsearch5131_data)
    else:
        st.error("No data available from customsearch5131.")


# Tab 2: View Shopify Products
with tabs[1]:
    st.subheader("Shopify Products")
    shopify_products = pd.DataFrame(get_shopify_products())
    if not shopify_products.empty:
        st.dataframe(shopify_products)
    else:
        st.error("No products available from Shopify.")

# Tab 3: Inventory Sync (SuiteQL)
with tabs[2]:
    st.subheader("Inventory Sync - NetSuite and Shopify by Title")
    match_netsuite_shopify_by_title()

# Tab 4: Post Products to Shopify (Unchanged for now)
with tabs[3]:
    st.subheader("Post Products from NetSuite to Shopify")
    if not customsearch5131_data.empty:
        selected_product = st.selectbox("Select Product to Post", customsearch5131_data['Title'])
        if st.button("Post to Shopify"):
            # Logic for posting to Shopify would go here
            st.success(f"Product {selected_product} posted to Shopify.")
    else:
        st.error("No products available from NetSuite to post.")
