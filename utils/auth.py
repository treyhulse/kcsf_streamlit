import streamlit as st
# auth.py

# Dictionary to store roles and their corresponding emails
roles = {
    'Sales Specialist': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Sales Manager': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Financial': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Administrator': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Shop Specialist': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Shop Manager': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Purchasing Specialist': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Purchasing Manager': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Marketing': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.com'],
    'Developer': ['trey.hulse@kcstorefixtures.com', 'treyhulse3@gmail.com'],
}

# Function to validate if an email has a specific role
def has_role(email, role):
    return email in roles.get(role, [])

# Function to check if an email has any role in a list of roles
def has_any_role(email, role_list):
    return any(has_role(email, role) for role in role_list)

# Function to get the role of a user by their email
def get_user_role(email):
    for role, emails in roles.items():
        if email in emails:
            return role
    return None

# Function to capture the user's email using st.experimental_user
def capture_user_email():
    user_info = st.experimental_user
    if user_info is not None:
        return user_info['email']
    else:
        return None

# Function to check if the user's role allows access to the page
def validate_access(email, allowed_roles=None, denied_roles=None):
    user_role = get_user_role(email)

    # If there are specific allowed roles, check if the user's role is one of them
    if allowed_roles is not None and user_role not in allowed_roles:
        return False

    # If there are specific denied roles, check if the user's role is one of them
    if denied_roles is not None and user_role in denied_roles:
        return False

    # If neither condition matches, grant access
    return True

# Universal permission violation message
def show_permission_violation():
    st.error("You do not have permission to view this page.")
    st.stop()

# Function to get sidebar content for a specific role
def get_sidebar_content(role):
    content = {
        'Sales Specialist': ["Sales", "Leads", "Opportunities"],
        'Sales Manager': ["Sales", "Team Performance", "Pipeline"],
        'Financial': ["Financial Reports", "Budgeting", "Expenses"],
        'Administrator': ["User Management", "Settings", "System Logs"],
        'Shop Specialist': ["Shop", "Work Orders", "Inventory"],
        'Shop Manager': ["Sales", "Team Assignments", "Efficiency"],
        'Purchasing Specialist': ["Supply Chain", "Purchase Orders", "Inventory Levels"],
        'Purchasing Manager': ["Supply Chain", "Supplier Performance", "Order Approvals"],
        'Marketing': ["Marketing", "Social Media", "Analytics"],
        'Developer': ["Shop", "Marketing", "Shipping Report", "Sales", "Logistics", "Showcase"],
    }
    return content.get(role, ["Default Content"])
