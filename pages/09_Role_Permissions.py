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
from pymongo import MongoClient
from utils.mongo_connection import get_mongo_client
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode
import pandas as pd

# Establish MongoDB connection
client = get_mongo_client()
db = client['netsuite']
roles_collection = db['roles']
permissions_collection = db['permissions']

def admin_ui():
    st.title("Role and Permissions Management")

    st.markdown("---")

    # Section 1: View and Edit Current Roles and Emails
    st.subheader("Current Roles and Emails")
    roles_data = list(roles_collection.find())
    
    # Convert MongoDB data to DataFrame
    roles_df = pd.DataFrame(roles_data)
    if not roles_df.empty:
        roles_df["_id"] = roles_df["_id"].astype(str)  # Convert ObjectId to string

    # Editable table using streamlit-aggrid
    gb = GridOptionsBuilder.from_dataframe(roles_df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Enable pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection('multiple', use_checkbox=True)  # Enable multi-row selection
    gb.configure_grid_options(editable=True)  # Make grid editable
    grid_options = gb.build()

    grid_response = AgGrid(
        roles_df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True,
        height=400,
        width='100%',
    )

    updated_df = grid_response['data']  # Get the DataFrame after editing
    selected_rows = grid_response['selected_rows']

    if st.button("Update Roles"):
        # Compare updated_df with roles_df to detect changes
        for index, row in updated_df.iterrows():
            original_row = roles_df.iloc[index]
            if not row.equals(original_row):  # Detect changes
                # Update MongoDB with the changes
                roles_collection.update_one(
                    {"_id": row["_id"]},
                    {"$set": {"role": row["role"], "emails": row["emails"]}}
                )
        st.success("Roles updated successfully.")

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
        emails_list = roles_collection.find_one({"role": role_selected})['emails']
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

if __name__ == "__main__":
    user_email = capture_user_email()
    if user_email is None:
        st.error("Unable to retrieve user information.")
        st.stop()

    page_name = '09_Role_Permissions.py'

    if validate_page_access(user_email, page_name):
        admin_ui()
    else:
        show_permission_violation()
