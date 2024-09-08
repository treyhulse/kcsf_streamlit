import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
from utils.suiteql import fetch_suiteql_data

# Page Title
st.title("Custom SuiteQL Query Builder")

# Step 1: Select Fields (Item-specific fields only)
st.subheader("1. Select Fields")
available_fields = [
    "item", "location", "quantityonhand", "quantityavailable", "status", "tranid"
]
selected_fields = st.multiselect(
    "Choose the fields you want to retrieve:", available_fields, default=["item", "quantityonhand", "quantityavailable"]
)

# Step 2: Define Filters (Item-specific)
st.subheader("2. Define Filters")

# Filter for Item ID (required)
item_filter = st.text_input("Enter Item ID (Required)", value="")

# Filter for Location (optional)
location_filter = st.text_input("Enter Location ID (Optional)", value="")

# Filter for Minimum Quantity on Hand
min_quantity_filter = st.number_input("Minimum Quantity On Hand (Optional)", min_value=0, value=0)

# Filter for Minimum Quantity Available
min_quantity_available_filter = st.number_input("Minimum Quantity Available (Optional)", min_value=0, value=0)

# Step 3: Sorting Options
st.subheader("3. Sorting and Limit")
sort_field = st.selectbox("Sort by Field", options=available_fields, index=0)
sort_order = st.radio("Sort Order", ("ASC", "DESC"))
limit_results = st.number_input("Limit number of results (Optional)", min_value=1, value=100)

# Step 4: Build the Query String
st.subheader("4. Generated Query")
query_conditions = []

# Add Item filter as it's required, assuming it's a numeric field, so no quotes around the value
if item_filter:
    query_conditions.append(f"item = {item_filter}")

# Add Location filter if provided, assuming it's a numeric field, so no quotes around the value
if location_filter:
    query_conditions.append(f"location = {location_filter}")

# Add minimum quantity on hand filter if provided
if min_quantity_filter > 0:
    query_conditions.append(f"quantityonhand >= {min_quantity_filter}")

# Add minimum quantity available filter if provided
if min_quantity_available_filter > 0:
    query_conditions.append(f"quantityavailable >= {min_quantity_available_filter}")

# Build WHERE clause
where_clause = " AND ".join(query_conditions) if query_conditions else ""

# Build the full SuiteQL query string
query = f"SELECT {', '.join(selected_fields)} FROM InventoryBalance"
if where_clause:
    query += f" WHERE {where_clause}"
query += f" ORDER BY {sort_field} {sort_order} LIMIT {limit_results}"

# Display the generated query
st.code(query, language="sql")

# Step 5: Execute the Query
if st.button("Run Query"):
    df = fetch_suiteql_data(query)
    
    if not df.empty:
        st.write(f"Results for your query:")
        st.dataframe(df)
    else:
        st.error("No data found for your query.")
