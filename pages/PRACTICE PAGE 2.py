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

# Fetch SuiteQL inventory data
@st.cache_data(ttl=900)
def fetch_suiteql_data():
    return fetch_netsuite_inventory()

# Create the 4 tabs
tabs = st.tabs([
    "View NetSuite Products (Custom Search 5131)", 
    "View Shopify Products", 
    "Inventory Sync (SuiteQL)", 
    "Post Products to Shopify"
])

# Tab 1: View NetSuite Products (Custom Search 5131 + SuiteQL Join)
with tabs[0]:
    st.subheader("NetSuite Products - Custom Search 5131 & Inventory Sync")

    # Fetch data from SuiteQL and the custom search
    customsearch5131_data = fetch_customsearch5131_data()
    suiteql_inventory = fetch_suiteql_data()

    # Check if data is available for both
    if not customsearch5131_data.empty and not suiteql_inventory.empty:
        # Perform the join on item_id (SuiteQL) and Title (saved search)
        joined_data = pd.merge(
            suiteql_inventory, customsearch5131_data, 
            left_on='item_id', right_on='Title', 
            how='inner'
        )
        
        # Display the joined data
        if not joined_data.empty:
            st.write(f"Joined {len(joined_data)} products between SuiteQL and customsearch5131.")
            st.dataframe(joined_data)
        else:
            st.error("No matches found between SuiteQL and customsearch5131 based on item_id and Title.")
    else:
        st.error("No data available for either SuiteQL or customsearch5131.")


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
    st.subheader("Inventory Sync (SuiteQL)")
    if not suiteql_inventory.empty:
        st.dataframe(suiteql_inventory)
    else:
        st.error("No inventory data available from SuiteQL.")

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
