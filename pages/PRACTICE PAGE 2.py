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
from utils.apis import get_netsuite_products_via_restlet, get_shopify_products, post_product_to_shopify, update_inventory_and_price

st.title("NetSuite & Shopify Product Sync")

# Define tabs for each functionality
tabs = st.tabs([
    "View NetSuite Products", 
    "View Shopify Products", 
    "Post Products to Shopify", 
    "Sync Inventory & Price"
])

# Tab 1: View NetSuite Products
with tabs[0]:
    st.subheader("NetSuite Products Marked for Shopify")
    
    # Fetch NetSuite products marked for Shopify
    netsuite_products = get_netsuite_products_via_restlet("customsearch0413")
    
    # Display the products
    if netsuite_products and not netsuite_products.empty:
        st.dataframe(netsuite_products)
    else:
        st.error("No products available from NetSuite.")

# Tab 2: View Shopify Products
with tabs[1]:
    st.subheader("Shopify Products")
    
    # Fetch Shopify products
    shopify_products = get_shopify_products()
    
    # Display Shopify products
    if shopify_products and not shopify_products.empty:
        st.dataframe(shopify_products)
    else:
        st.error("No products available from Shopify.")

# Tab 3: Post Products to Shopify
with tabs[2]:
    st.subheader("Post Products from NetSuite to Shopify")
    
    # Display NetSuite products for selection
    if netsuite_products and not netsuite_products.empty:
        selected_product = st.selectbox("Select Product to Post", netsuite_products['itemId'])
        
        if st.button("Post to Shopify"):
            # Prepare the data for Shopify
            product_data = {
                "product": {
                    "title": selected_product,
                    "body_html": netsuite_products.loc[netsuite_products['itemId'] == selected_product, 'description'].values[0],
                    "variants": [
                        {
                            "price": netsuite_products.loc[netsuite_products['itemId'] == selected_product, 'price'].values[0],
                            "sku": netsuite_products.loc[netsuite_products['itemId'] == selected_product, 'sku'].values[0]
                        }
                    ]
                }
            }
            status_code, response = post_product_to_shopify(product_data)
            
            if status_code == 201:
                st.success("Product posted successfully!")
            else:
                st.error(f"Failed to post product. Response: {response}")
    else:
        st.error("No NetSuite products available to post.")

# Tab 4: Sync Inventory & Price
with tabs[3]:
    st.subheader("Sync Inventory & Price between NetSuite and Shopify")
    
    # Display Shopify products for selection
    if shopify_products and not shopify_products.empty:
        selected_shopify_product = st.selectbox("Select Shopify Product to Update", shopify_products['title'])
        
        # Input fields for new price and inventory quantity
        new_price = st.number_input("New Price", min_value=0.0)
        new_inventory = st.number_input("New Inventory Quantity", min_value=0)
        
        if st.button("Update Product"):
            product_id = shopify_products.loc[shopify_products['title'] == selected_shopify_product, 'id'].values[0]
            status_code, response = update_inventory_and_price(product_id, new_inventory, new_price)
            
            if status_code == 200:
                st.success("Product updated successfully!")
            else:
                st.error(f"Failed to update product. Response: {response}")
    else:
        st.error("No Shopify products available for update.")
