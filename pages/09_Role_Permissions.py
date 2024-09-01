import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '09_Role_Permissions.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
from bson.objectid import ObjectId
from utils.mongo_connection import get_mongo_client, get_collection_data

# Initialize MongoDB client
client = get_mongo_client()

# Function to display an editable table and update MongoDB
def display_editable_table(collection_name):
    st.subheader(f"{collection_name.capitalize()} Collection")
    
    # Fetch data from MongoDB
    df = get_collection_data(client, collection_name)
    
    if not df.empty:
        df["_id"] = df["_id"].astype(str)  # Convert ObjectId to string for display

    # Create an editable form for each row
    updated_rows = []
    with st.form(key=f"{collection_name}_form"):
        for index, row in df.iterrows():
            with st.expander(f"Edit Row {index + 1}"):
                updated_row = {}
                updated_row["_id"] = row["_id"]
                updated_row["roles"] = st.text_input(f"Role {index + 1}", value=row["role"])
                updated_row["emails"] = st.text_area(f"Emails {index + 1}", value=row["emails"])
                updated_rows.append(updated_row)
        
        submit_button = st.form_submit_button(label="Publish Changes")
    
    # Update MongoDB when the form is submitted
    if submit_button:
        collection = client['netsuite'][collection_name]
        for updated_row in updated_rows:
            # Update MongoDB document by _id
            collection.update_one(
                {"_id": ObjectId(updated_row["_id"])},
                {"$set": {"role": updated_row["role"], "emails": updated_row["emails"]}}
            )
        st.success(f"Changes published to {collection_name.capitalize()} collection.")

# Streamlit app layout
st.title("MongoDB Editable Table")

st.markdown("### Edit Roles and Permissions Collections")

# Display editable table for Roles collection
display_editable_table('roles')

st.markdown("---")

# Display editable table for Permissions collection
display_editable_table('permissions')
