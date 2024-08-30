import streamlit as st

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

    # If neither condition matches, grant access (default to allow access)
    return True

# Universal permission violation message
def show_permission_violation():
    st.error("You do not have permission to view this page.")
    st.stop()

# Function to get sidebar content for a specific role
def get_sidebar_content(role):
    content = {
        'Sales Specialist': ["Sales", "Leads", "Opportunities", "Shop", "Marketing", "Shipping Report", "Logistics", "Showcase"],
        'Sales Manager': ["Sales", "Team Performance", "Pipeline", "Shop", "Marketing", "Shipping Report", "Logistics", "Showcase"],
        'Financial': ["Financial Reports", "Budgeting", "Expenses", "Shop", "Marketing", "Shipping Report", "Logistics", "Showcase"],
        'Administrator': ["User Management", "Settings", "System Logs", "Sales", "Shop", "Marketing", "Shipping Report", "Logistics", "Showcase"],
        'Shop Specialist': ["Shop", "Work Orders", "Inventory", "Sales", "Marketing", "Shipping Report", "Logistics", "Showcase"],
        'Shop Manager': ["Sales", "Team Assignments", "Efficiency", "Shop", "Marketing", "Shipping Report", "Logistics", "Showcase"],
        'Purchasing Specialist': ["Supply Chain", "Purchase Orders", "Inventory Levels", "Shop", "Marketing", "Shipping Report", "Logistics", "Showcase"],
        'Purchasing Manager': ["Supply Chain", "Supplier Performance", "Order Approvals", "Shop", "Marketing", "Shipping Report", "Logistics", "Showcase"],
        'Marketing': ["Marketing", "Social Media", "Analytics", "Shop", "Sales", "Shipping Report", "Logistics", "Showcase"],
        'Developer': ["Shop", "Marketing", "Shipping Report", "Sales", "Logistics", "Showcase", "Financial Reports", "User Management", "System Logs"],
    }
    return content.get(role, ["Default Content"])

# Mapping of pages to roles (all roles have access by default)
page_access = {
    '01_Shipping Report.py': ['Sales Specialist', 'Sales Manager', 'Financial', 'Administrator', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
    '02_Supply_Chain.py': ['Sales Specialist', 'Sales Manager', 'Financial', 'Administrator', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
    '03_Marketing.py': ['Sales Specialist', 'Sales Manager', 'Financial', 'Administrator', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
    '03_Sales.py': ['Sales Specialist', 'Sales Manager', 'Financial', 'Administrator', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
    '05_Shop.py': ['Sales Specialist', 'Sales Manager', 'Financial', 'Administrator', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
    '06_Logistics.py': ['Sales Specialist', 'Sales Manager', 'Financial', 'Administrator', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
    '07_AI_Insights.py': ['Sales Specialist', 'Sales Manager', 'Financial', 'Administrator', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
    '08_Showcase.py': ['Sales Specialist', 'Sales Manager', 'Financial', 'Administrator', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
}

# Function to validate if a user can access a specific page
def validate_page_access(email, page_name):
    user_role = get_user_role(email)
    allowed_roles = page_access.get(page_name, [])

    if user_role in allowed_roles:
        return True
    else:
        return False
