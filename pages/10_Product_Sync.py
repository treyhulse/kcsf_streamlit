import streamlit as st
from utils.auth import validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Check for user email in query parameters first
query_params = st.experimental_get_query_params()
user_email = query_params.get('email', [None])[0]

# Fallback: Check if the request is coming from your NetSuite domain
def is_netsuite_request():
    referer = st.experimental_get_query_params().get('Referer')
    return referer and '3429264.app.netsuite.com' in referer[0]

# If email is still None, and it's from NetSuite, use a placeholder email
if user_email is None and is_netsuite_request():
    user_email = "netsuite_user@yourdomain.com"

# Check if email was passed and is valid
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Product Sync'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")




################################################################################################

## AUTHENTICATED

################################################################################################


from utils.apis import get_netsuite_products_via_restlet, get_shopify_products, post_product_to_shopify, update_inventory_and_price

st.title("NetSuite & Shopify Product Sync")

tabs = st.tabs(["View NetSuite Products", "View Shopify Products", "Post Products", "Update Inventory & Price"])

# Tab 1: View NetSuite Products
with tabs[0]:
    st.header("NetSuite Products Marked for Shopify")
    netsuite_products = get_netsuite_products_via_restlet()
    if netsuite_products:
        st.table(netsuite_products)
    else:
        st.error("No products available from NetSuite.")

# Tab 2: View Shopify Products
with tabs[1]:
    st.header("Shopify Products")
    shopify_products = get_shopify_products()
    if shopify_products:
        st.table(shopify_products)
    else:
        st.error("No products available from Shopify.")

# Tab 3: Post Products to Shopify
with tabs[2]:
    st.header("Post Products from NetSuite to Shopify")
    if netsuite_products:
        selected_product = st.selectbox("Select Product to Post", netsuite_products)
        if st.button("Post to Shopify"):
            product_data = {
                "product": {
                    "title": selected_product['itemId'],  # Adjust based on your saved search results
                    "body_html": selected_product['description'],
                    "variants": [{"price": selected_product['price'], "sku": selected_product['sku']}]
                }
            }
            status_code, response = post_product_to_shopify(product_data)
            if status_code == 201:
                st.success("Product posted successfully!")
            else:
                st.error(f"Failed to post product. Response: {response}")
    else:
        st.error("No products available to post.")

# Tab 4: Update Inventory & Price
with tabs[3]:
    st.header("Update Shopify Product Inventory & Price")
    if shopify_products:
        selected_shopify_product = st.selectbox("Select Product to Update", shopify_products)
        new_price = st.number_input("New Price", min_value=0.0)
        new_inventory = st.number_input("New Inventory Quantity", min_value=0)
        if st.button("Update Product"):
            status_code, response = update_inventory_and_price(
                selected_shopify_product['id'], new_inventory, new_price
            )
            if status_code == 200:
                st.success("Product updated successfully!")
            else:
                st.error(f"Failed to update product. Response: {response}")
    else:
        st.error("No Shopify products available for update.")
