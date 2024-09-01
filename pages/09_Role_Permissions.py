import streamlit as st
from pymongo import MongoClient
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.mongo_connection import get_mongo_client
from bson.objectid import ObjectId
import ast  # Importing ast to safely evaluate strings

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

# Establish MongoDB connection
client = get_mongo_client()
db = client['netsuite']
roles_collection = db['roles']
permissions_collection = db['permissions']

def display_editable_table(collection_name):
    st.subheader(f"{collection_name.capitalize()} Collection")
    
    # Fetch data from MongoDB
    df = pd.DataFrame(list(db[collection_name].find()))
    
    if not df.empty:
        df["_id"] = df["_id"].astype(str)  # Convert ObjectId to string for display

    # Create an editable form for each row
    updated_rows = []
    with st.form(key=f"{collection_name}_form"):
        for index, row in df.iterrows():
            with st.expander(f"Edit Row {index + 1}"):
                updated_row = {}
                updated_row["_id"] = row["_id"]
                
                if collection_name == "roles":
                    # Convert the emails string back to a list if it's stored as a string
                    emails_list = ast.literal_eval(row.get("emails", "[]"))
                    emails_str = "\n".join(emails_list)
                    updated_row["role"] = st.text_input(f"Role {index + 1}", value=row.get("role", ""))
                    updated_row["emails"] = st.text_area(f"Emails {index + 1}", value=emails_str)
                
                elif collection_name == "permissions":
                    # Edit the 'permissions' collection
                    updated_row["page"] = st.text_input(f"Page {index + 1}", value=row.get("page", ""))
                    
                    # For 'roles', allow the user to edit the list of roles
                    roles_str = "\n".join(row.get("roles", []))  # Convert list to string for textarea
                    updated_roles_str = st.text_area(f"Roles {index + 1} (one per line)", value=roles_str)
                    updated_row["roles"] = [role.strip() for role in updated_roles_str.split("\n") if role.strip()]
                
                updated_rows.append(updated_row)
        
        submit_button = st.form_submit_button(label="Publish Changes")
    
    # Update MongoDB when the form is submitted
    if submit_button:
        collection = client['netsuite'][collection_name]
        for updated_row in updated_rows:
            # Convert emails back to a list for storage
            if collection_name == "roles":
                updated_row["emails"] = [email.strip() for email in updated_row["emails"].split("\n") if email.strip()]
            
            # Update MongoDB document by _id
            collection.update_one(
                {"_id": ObjectId(updated_row["_id"])},
                {"$set": updated_row}
            )
        st.success(f"Changes published to {collection_name.capitalize()} collection.")

def admin_ui():
    st.title("Role and Permissions Management")

    st.markdown("---")

    # Section 1: View Current Roles and Emails
    st.subheader("Current Roles and Emails")
    roles_data = roles_collection.find()
    for role in roles_data:
        # Convert emails from string to list for display
        emails_list = ast.literal_eval(role["emails"])
        st.write(f"**{role['role']}**: {', '.join(emails_list)}")

    st.markdown("---")

    # Section 2: Add a New Role or Email
    st.subheader("Add New Role or Email")
    add_option = st.radio("Choose an option:", ("Add New Role", "Add Email to Existing Role"))

    if add_option == "Add New Role":
        new_role = st.text_input("Enter new role name")
        new_emails = st.text_area("Enter emails for this role (one per line)")
        if st.button("Add Role"):
            emails_list = [email.strip() for email in new_emails.split('\n') if email.strip()]
            roles_collection.insert_one({"role": new_role, "emails": emails_list})
            st.success(f"Role '{new_role}' added with {len(emails_list)} email(s).")

    elif add_option == "Add Email to Existing Role":
        existing_role = st.selectbox("Select role to add email to", [role['role'] for role in roles_collection.find()])
        new_email = st.text_input("Enter email to add")
        if st.button("Add Email"):
            roles_collection.update_one({"role": existing_role}, {"$addToSet": {"emails": new_email}})
            st.success(f"Email '{new_email}' added to role '{existing_role}'.")

    st.markdown("---")

    # Section 3: Remove a Role or Email
    st.subheader("Remove Role or Email")
    remove_option = st.radio("Choose an option:", ("Remove Entire Role", "Remove Email from Role"))

    if remove_option == "Remove Entire Role":
        role_to_remove = st.selectbox("Select role to remove", [role['role'] for role in roles_collection.find()])
        if st.button("Remove Role"):
            roles_collection.delete_one({"role": role_to_remove})
            st.success(f"Role '{role_to_remove}' has been removed.")

    elif remove_option == "Remove Email from Role":
        role_selected = st.selectbox("Select role", [role['role'] for role in roles_collection.find()])
        emails_list = ast.literal_eval(roles_collection.find_one({"role": role_selected})['emails'])
        email_selected = st.selectbox("Select email to remove", emails_list)
        if st.button("Remove Email"):
            roles_collection.update_one({"role": role_selected}, {"$pull": {"emails": email_selected}})
            st.success(f"Email '{email_selected}' has been removed from role '{role_selected}'.")

    st.markdown("---")

    # Section 4: Update Page Access Permissions
    st.subheader("Update Page Access Permissions")
    selected_page = st.selectbox("Select page to update access for", [perm['page'] for perm in permissions_collection.find()])
    permission_entry = permissions_collection.find_one({"page": selected_page})
    current_roles = permission_entry['roles'] if permission_entry else []
    all_roles = [role['role'] for role in roles_collection.find()]
    
    # Ensure default roles are valid options
    valid_roles = [role for role in current_roles if role in all_roles]
    
    selected_roles = st.multiselect(
        "Select roles that can access this page",
        all_roles,
        default=valid_roles
    )

    if st.button("Update Page Access"):
        permissions_collection.update_one(
            {"page": selected_page},
            {"$set": {"roles": selected_roles}},
            upsert=True
        )
        st.success(f"Access permissions for page '{selected_page}' have been updated.")

    st.markdown("---")

    # Section 5: Editable Tables
    st.subheader("Edit Roles and Permissions Collections")
    
    # Editable table for Roles collection
    display_editable_table('roles')

    st.markdown("---")

    # Editable table for Permissions collection
    display_editable_table('permissions')

if __name__ == "__main__":
    admin_ui()
