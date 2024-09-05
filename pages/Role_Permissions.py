import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Role Permissions'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from utils.mongo_connection import get_mongo_client
from bson.objectid import ObjectId
import ast

# Establish MongoDB connection
client = get_mongo_client()
db = client['netsuite']
roles_collection = db['roles']
permissions_collection = db['permissions']

def display_editable_table(collection_name, table_title):
    st.subheader(table_title)
    
    # Fetch data from MongoDB
    df = pd.DataFrame(list(db[collection_name].find()))
    
    if not df.empty:
        df["_id"] = df["_id"].astype(str)  # Convert ObjectId to string for display

    # Create an editable form for each row
    updated_rows = []
    with st.form(key=f"{collection_name}_form"):
        for index, row in df.iterrows():
            if collection_name == "roles":
                expander_label = f"{row.get('role', 'Unknown Role')}"
            elif collection_name == "permissions":
                expander_label = f"{row.get('page', 'Unknown Page')}"

            with st.expander(expander_label):
                updated_row = {}
                updated_row["_id"] = row["_id"]
                
                if collection_name == "roles":
                    # Handle the emails field correctly
                    emails = row.get("emails", "")
                    if isinstance(emails, str):
                        try:
                            # Attempt to parse a stringified list if it exists
                            emails_list = ast.literal_eval(emails)
                        except:
                            emails_list = [email.strip() for email in emails.split(',')]
                    elif isinstance(emails, list):
                        emails_list = emails
                    else:
                        emails_list = []

                    emails_str = "\n".join(emails_list)
                    updated_row["role"] = st.text_input(f"Role Name", value=row.get("role", ""), key=f"role_name_{index}")
                    updated_row["emails"] = st.text_area(f"Role Emails (one per line)", value=emails_str, key=f"emails_{index}")
                
                elif collection_name == "permissions":
                    # Edit the 'permissions' collection with labels
                    updated_row["page"] = st.text_input(f"Page Name", value=row.get("page", ""), key=f"page_name_{index}")
                    
                    # For 'roles', allow the user to edit the list of roles
                    roles_str = "\n".join(row.get("roles", []))  # Convert list to string for textarea
                    updated_roles_str = st.text_area(f"Allowed Roles (one per line)", value=roles_str, key=f"roles_{index}")
                    updated_row["roles"] = [role.strip() for role in updated_roles_str.split("\n") if role.strip()]
                
                updated_rows.append(updated_row)
        
        submit_button = st.form_submit_button(label="Publish Changes")
    
    # Update MongoDB when the form is submitted
    if submit_button:
        collection = client['netsuite'][collection_name]
        try:
            for updated_row in updated_rows:
                # Convert emails back to a list for storage
                if collection_name == "roles":
                    updated_row["emails"] = [email.strip() for email in updated_row["emails"].split("\n") if email.strip()]
                
                # Do not modify the '_id' field during the update
                updated_row_to_save = {key: value for key, value in updated_row.items() if key != "_id"}

                # Update MongoDB document by _id
                collection.update_one(
                    {"_id": ObjectId(updated_row["_id"])},
                    {"$set": updated_row_to_save}
                )
            st.success(f"Changes published to {table_title}.")
        except Exception as e:
            st.error("An error occurred while updating the data.")

def admin_ui():
    st.title("Role and Permissions Management")

    st.markdown("---")

    # Editable table for Roles collection
    display_editable_table('roles', 'Roles Management')

    st.markdown("---")

    # Editable table for Permissions collection
    display_editable_table('permissions', 'Page Permissions')

if __name__ == "__main__":
    admin_ui()
