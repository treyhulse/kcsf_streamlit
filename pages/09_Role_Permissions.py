import streamlit as st
from utils.auth import roles, page_access, save_roles_to_file, save_page_access_to_file, has_role, capture_user_email, show_permission_violation, validate_page_access

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '01_Shipping Report.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################
import json

def admin_ui():
    st.title("Role and Permissions Management")

    st.markdown("---")

    # Section 1: View Current Roles and Emails
    st.subheader("Current Roles and Emails")
    for role, emails in roles.items():
        st.write(f"**{role}**: {', '.join(emails)}")

    st.markdown("---")

    # Section 2: Add a New Role or Email
    st.subheader("Add New Role or Email")
    add_option = st.radio("Choose an option:", ("Add New Role", "Add Email to Existing Role"))

    if add_option == "Add New Role":
        new_role = st.text_input("Enter new role name")
        new_emails = st.text_area("Enter emails for this role (one per line)")
        if st.button("Add Role"):
            if new_role and new_emails:
                email_list = [email.strip() for email in new_emails.split('\n') if email.strip()]
                if new_role in roles:
                    st.warning(f"Role '{new_role}' already exists.")
                else:
                    roles[new_role] = email_list
                    save_roles_to_file()
                    st.success(f"Role '{new_role}' added with {len(email_list)} email(s).")
            else:
                st.error("Please provide both role name and at least one email.")

    elif add_option == "Add Email to Existing Role":
        if roles:
            existing_role = st.selectbox("Select role to add email to", list(roles.keys()))
            new_email = st.text_input("Enter email to add")
            if st.button("Add Email"):
                if existing_role and new_email:
                    if new_email in roles[existing_role]:
                        st.warning(f"Email '{new_email}' is already associated with '{existing_role}'.")
                    else:
                        roles[existing_role].append(new_email)
                        save_roles_to_file()
                        st.success(f"Email '{new_email}' added to role '{existing_role}'.")
                else:
                    st.error("Please select a role and enter an email.")
        else:
            st.info("No roles available. Please add a new role first.")

    st.markdown("---")

    # Section 3: Remove a Role or Email
    st.subheader("Remove Role or Email")
    remove_option = st.radio("Choose an option:", ("Remove Entire Role", "Remove Email from Role"))

    if remove_option == "Remove Entire Role":
        if roles:
            role_to_remove = st.selectbox("Select role to remove", list(roles.keys()))
            if st.button("Remove Role"):
                confirm = st.warning(f"Are you sure you want to remove the role '{role_to_remove}'?", icon="⚠️")
                if st.button("Yes, Remove"):
                    del roles[role_to_remove]
                    save_roles_to_file()
                    st.success(f"Role '{role_to_remove}' has been removed.")
        else:
            st.info("No roles available to remove.")

    elif remove_option == "Remove Email from Role":
        if roles:
            role_selected = st.selectbox("Select role", list(roles.keys()))
            if roles[role_selected]:
                email_selected = st.selectbox("Select email to remove", roles[role_selected])
                if st.button("Remove Email"):
                    roles[role_selected].remove(email_selected)
                    if not roles[role_selected]:
                        del roles[role_selected]
                        st.info(f"Role '{role_selected}' has no more emails and has been removed.")
                    save_roles_to_file()
                    st.success(f"Email '{email_selected}' has been removed from role '{role_selected}'.")
            else:
                st.info(f"Role '{role_selected}' has no emails to remove.")
        else:
            st.info("No roles available.")

    st.markdown("---")

    # Section 4: Update Page Access Permissions
    st.subheader("Update Page Access Permissions")
    selected_page = st.selectbox("Select page to update access for", list(page_access.keys()))
    current_roles = page_access.get(selected_page, [])
    selected_roles = st.multiselect("Select roles that can access this page", list(roles.keys()), default=current_roles)
    if st.button("Update Page Access"):
        page_access[selected_page] = selected_roles
        save_page_access_to_file()
        st.success(f"Access permissions for '{selected_page}' have been updated.")

if __name__ == "__main__":
    # Capture the user's email
    user_email = capture_user_email()
    if user_email is None:
        st.error("Unable to retrieve user information.")
        st.stop()

    # Validate access to this specific page
    page_name = '09_Role_Permissions.py'  # Current page name
    if not validate_page_access(user_email, page_name):
        show_permission_violation()

    # If the user is an Administrator, show the admin UI
    if has_role(user_email, 'Administrator'):
        admin_ui()
    else:
        show_permission_violation()
