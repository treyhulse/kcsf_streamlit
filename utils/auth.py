import streamlit as st

# Dictionary to store roles and their corresponding emails
roles = {
    'Sales Specialist': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
    'Sales Manager': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
    'Financial': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
    'Administrator': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
    'Shop Specialist': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
    'Shop Manager': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
    'Purchasing Specialist': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
    'Purchasing Manager': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
    'Marketing': ['trey.hulse@kcstorefixtures.co', 'treyhulse3@gmail.co'],
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

# Function to dynamically build the sidebar based on the user's role and return the selected page
def build_sidebar(role):
    sidebar_content = {
        'Sales Specialist': {
            "header": "Sales Tools",
            "items": {
                "Home": "streamlit_app.py",
                "Sales": "02_Sales.py",
                "Marketing": "03_Marketing.py"
            }
        },
        'Sales Manager': {
            "header": "Manager Tools",
            "items": {
                "Team Performance": "03_Sales.py",
                "Pipeline": "03_Sales.py",
                "Sales": "03_Sales.py"
            }
        },
        'Financial': {
            "header": "Financial Tools",
            "items": {
                "Financial Reports": "03_Sales.py",
                "Budgeting": "03_Sales.py",
                "Expenses": "03_Sales.py"
            }
        },
        'Administrator': {
            "header": "Admin Tools",
            "items": {
                "User Management": "03_Sales.py",
                "Settings": "03_Sales.py",
                "System Logs": "03_Sales.py"
            }
        },
        'Shop Specialist': {
            "header": "Shop Tools",
            "items": {
                "Shop": "05_Shop.py",
                "Work Orders": "05_Shop.py",
                "Inventory": "05_Shop.py"
            }
        },
        'Shop Manager': {
            "header": "Manager Tools",
            "items": {
                "Team Assignments": "05_Shop.py",
                "Efficiency": "05_Shop.py",
                "Shop": "05_Shop.py"
            }
        },
        'Purchasing Specialist': {
            "header": "Purchasing Tools",
            "items": {
                "Supply Chain": "02_Supply_Chain.py",
                "Purchase Orders": "02_Supply_Chain.py",
                "Inventory Levels": "02_Supply_Chain.py"
            }
        },
        'Purchasing Manager': {
            "header": "Manager Tools",
            "items": {
                "Supplier Performance": "02_Supply_Chain.py",
                "Order Approvals": "02_Supply_Chain.py",
                "Supply Chain": "02_Supply_Chain.py"
            }
        },
        'Marketing': {
            "header": "Marketing Tools",
            "items": {
                "Campaigns": "03_Marketing.py",
                "Social Media": "03_Marketing.py",
                "Analytics": "03_Marketing.py"
            }
        },
        'Developer': {
            "header": "Developer Tools",
            "items": {
                "Shipping Report": "01_Shipping_Report.py",
                "Supply Chain": "02_Supply_Chain.py",
                "Marketing": "03_Marketing.py"
            }
        },
    }

    # Get the content for the current role
    content = sidebar_content.get(role, {"header": "Tools", "items": {"Default Content": None}})

    # Build the sidebar using Streamlit's sidebar components
    st.sidebar.title(content["header"])
    selected_page = st.sidebar.radio("Navigate to", list(content["items"].keys()))

    # Return the selected page's file name
    return content["items"][selected_page]

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
