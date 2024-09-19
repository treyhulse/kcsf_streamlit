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

# Import necessary libraries and functions
import streamlit as st
import pandas as pd
from utils.restlet import fetch_restlet_data  # Pulls data from RESTlet for customsearch
from utils.suiteql import fetch_netsuite_inventory  # For SuiteQL inventory sync
from utils.apis import get_shopify_products
from utils.shopify_connection import sku_exists_on_shopify, prepare_product_data, post_product_to_shopify, get_synced_products_from_shopify


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

# Tab 1: View NetSuite Products (Custom Search 5131 + SuiteQL Join with Aggregated Inventory)
with tabs[0]:
    st.subheader("NetSuite Products - Custom Search 5131 & Aggregated Inventory Sync")

    # Fetch data from SuiteQL and the custom search
    customsearch5131_data = fetch_customsearch5131_data()
    suiteql_inventory = fetch_suiteql_data()

    # Check if data is available for both
    if not customsearch5131_data.empty and not suiteql_inventory.empty:
        # Convert SuiteQL `display_name` to string to match with `Title` from saved search
        suiteql_inventory['display_name'] = suiteql_inventory['display_name'].astype(str)
        customsearch5131_data['Title'] = customsearch5131_data['Title'].astype(str)

        # Convert `quantity_available` to numeric to allow aggregation
        suiteql_inventory['quantity_available'] = pd.to_numeric(suiteql_inventory['quantity_available'], errors='coerce')

        # Perform the join on display_name (SuiteQL) and Title (saved search)
        joined_data = pd.merge(
            suiteql_inventory, customsearch5131_data, 
            left_on='display_name', right_on='Title', 
            how='inner'
        )

        # Aggregate by display_name/Title and sum the quantity_available
        aggregated_data = joined_data.groupby(['display_name', 'Title']).agg({
            'quantity_available': 'sum',  # Sum the numeric quantity_available for each item
            'Description': 'first', 
            'Price': 'first',
            # Add more fields as needed
        }).reset_index()

        # Display the aggregated data
        if not aggregated_data.empty:
            st.write(f"Aggregated {len(aggregated_data)} products with total inventory from SuiteQL and customsearch5131.")
            st.dataframe(aggregated_data)
        else:
            st.error("No matches found after aggregation.")
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

# Tab 3: Inventory Sync (SuiteQL with Item Type and Assembly Items)
with tabs[2]:
    st.subheader("Inventory Sync (SuiteQL with Item Type and Assembly Items)")
    
    # Fetch SuiteQL data with item_type and assembly items included in the query
    suiteql_inventory = fetch_suiteql_data()  # Ensure the SuiteQL query includes 'item_type' and assembly items

    if not suiteql_inventory.empty:
        # Display the SuiteQL data including item_type
        st.dataframe(suiteql_inventory)
    else:
        st.error("No inventory data available from SuiteQL.")


# Tab 4: Post Products to Shopify (Enhanced with Shopify Comparison)
with tabs[3]:
    st.subheader("Post Products from NetSuite to Shopify")
    
    # Fetch data from customsearch5131
    customsearch5131_data = fetch_customsearch5131_data()

    # Fetch all products from Shopify
    shopify_products = get_synced_products_from_shopify()

    # Extract all SKUs from Shopify products
    shopify_skus = []
    if shopify_products:
        for product in shopify_products:
            for variant in product.get('variants', []):
                shopify_skus.append(variant.get('sku', ''))
        shopify_skus = [sku for sku in shopify_skus if sku]  # Filter out empty SKUs

    if not customsearch5131_data.empty:
        # Select a product to post based on SKU
        selected_product = st.selectbox("Select Product to Post", customsearch5131_data['Title'])
        
        # Get the row data for the selected product
        selected_row = customsearch5131_data[customsearch5131_data['Title'] == selected_product].iloc[0]
        
        # Display selected product details
        st.write("Selected Product Details:")
        st.write(f"SKU: {selected_row['SKU']}")
        st.write(f"Description: {selected_row['Description']}")
        st.write(f"Price: {selected_row['Price']}")
        
        # Check if the SKU exists in the Shopify SKUs list
        if selected_row['SKU'] in shopify_skus:
            st.warning(f"Product with SKU {selected_row['SKU']} already exists on Shopify.")
        else:
            # Prepare product data for Shopify
            product_data = prepare_product_data(
                item_name=selected_row['Title'],
                description=selected_row['Description'],
                price=selected_row['Price'],
                sku=selected_row['SKU']
            )

            # Post the product to Shopify
            if st.button("Post to Shopify"):
                post_product_to_shopify(product_data)
    else:
        st.error("No products available from NetSuite to post.")