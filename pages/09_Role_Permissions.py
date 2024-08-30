import streamlit as st
import json
from utils.auth import roles, page_access, has_role, capture_user_email, show_permission_violation

# Function to save roles to a JSON file
def save_roles_to_file():
    with open('roles.json', 'w') as f:
        json.dump(roles, f)

# Function to save page access to a JSON file
def save_page_access_to_file():
    with open('page_access.json', 'w') as f:
        json.dump(page_access, f)

# Function to load roles from a JSON file
def load_roles_from_file():
    global roles
    try:
        with open('roles.json', 'r') as f:
            roles = json.load(f)
    except FileNotFoundError:
        save_roles_to_file()  # Create the file if it doesn't exist

# Function to load page access from a JSON file
def load_page_access_from_file():
    global page_access
    try:
        with open('page_access.json', 'r') as f:
            page_access = json.load(f)
    except FileNotFoundError:
        save_page_access_to_file()  # Create the file if it doesn't exist

# Call these functions to load data at the start
load_roles_from_file()
load_page_access_from_file()

def admin_ui():
    st.title("Role and Permissions Management")

    # Display current roles and emails
    st.subheader("Current Roles and Emails")
    for role, emails in roles.items():
        st.write(f"**{role}**: {', '.join(emails)}")
    
    # Add a new role
    st.subheader("Add New Role")
    new_role = st.text_input("Enter new role name")
    new_email = st.text_input("Enter email for new role")
    if st.button("Add Role"):
        if new_role and new_email:
            if new_role in roles:
                if new_email not in roles[new_role]:
                    roles[new_role].append(new_email)
                    save_roles_to_file()
                    st.success(f"Role '{new_role}' updated with email '{new_email}'")
                else:
                    st.warning(f"Email '{new_email}' is already associated with the role '{new_role}'")
            else:
                roles[new_role] = [new_email]
                save_roles_to_file()
                st.success(f"Role '{new_role}' added with email '{new_email}'")
    
    # Remove a role or email
    st.subheader("Remove Role or Email")
    role_to_remove = st.selectbox("Select role to remove", list(roles.keys()))
    email_to_remove = st.selectbox("Select email to remove", roles.get(role_to_remove, []))
    if st.button("Remove Email"):
        if role_to_remove and email_to_remove:
            roles[role_to_remove].remove(email_to_remove)
            if not roles[role_to_remove]:  # Remove role if no emails left
                del roles[role_to_remove]
            save_roles_to_file()
            st.success(f"Email '{email_to_remove}' removed from role '{role_to_remove}'")

    # Update page access permissions
    st.subheader("Update Page Access Permissions")
    selected_page = st.selectbox("Select page", list(page_access.keys()))
    roles_for_page = st.multiselect("Select roles for this page", list(roles.keys()), default=page_access[selected_page])
    if st.button("Update Page Access"):
        page_access[selected_page] = roles_for_page
        save_page_access_to_file()
        st.success(f"Page '{selected_page}' access updated.")

if __name__ == "__main__":
    # Check if the user is an admin
    user_email = capture_user_email()
    if has_role(user_email, 'Administrator'):
        admin_ui()
    else:
        show_permission_violation()
