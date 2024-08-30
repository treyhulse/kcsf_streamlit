import streamlit as st

# Dictionary to store roles and their corresponding emails
roles = {
    'Administrator': ['trey.hulse@kcstorefixtures.com', 'treyhulse3@gmail.com', 'gina.bliss@kcstorefixtures.com'],
    'Sales Specialist': ['becky.dean@kcstorefixtures.com', 'treyhulse3@kcstorefixtures.com'],
    'Sales Manager': ['anna.alessi@kcstorefixtures.co', 'treyhulse3@kcstorefixtures.com'],
    'Financial': ['sean.castle@kcstorefixtures.co', 'treyhulse3@kcstorefixtures.com'],
    'Shop Specialist': ['victor@kc-store-fixtures.com', 'treyhulse3@kcstorefixtures.com'],
    'Shop Manager': ['tim@kc-store-fixtures.com', 'victor@kc-store-fixtures.com'],
    'Purchasing Specialist': ['matt@kc-store-fixtures.co', 'treyhulse3@kcstorefixtures.com'],
    'Purchasing Manager': ['mike@kc-store-fixtures.co', 'treyhulse3@kcstorefixtures.com'],
    'Marketing': ['robin.falk@kcstorefixtures.com', 'treyhulse3@kcstorefixtures.com'],
}

# Function to validate if an email has a specific role
def has_role(email, role):
    return email in roles.get(role, [])

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

# Mapping of pages to roles that have access
page_access = {
    '01_Shipping Report.py': ['Administrator', 'Sales Specialist', 'Sales Manager', 'Financial', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing'],
    '02_Supply_Chain.py': ['Administrator', 'Sales Specialist', 'Sales Manager', 'Financial', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing'],
    '03_Marketing.py': ['Administrator', 'Sales Specialist', 'Sales Manager', 'Financial', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing'],
    '03_Sales.py': ['Administrator', 'Sales Specialist', 'Sales Manager', 'Financial', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing'],
    '05_Shop.py': ['Administrator', 'Sales Specialist', 'Sales Manager', 'Financial', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing'],
    '06_Logistics.py': ['Administrator', 'Sales Specialist', 'Sales Manager', 'Financial', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing'],
    '07_AI_Insights.py': ['Administrator', 'Sales Specialist', 'Sales Manager', 'Financial', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing', 'Developer'],
    '08_Showcase.py': ['Administrator', 'Sales Specialist', 'Sales Manager', 'Financial', 'Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Marketing'],
}

# Function to validate if a user can access a specific page
def validate_page_access(email, page_name):
    user_role = get_user_role(email)
    allowed_roles = page_access.get(page_name, [])

    if user_role in allowed_roles:
        return True
    else:
        return False

# Universal permission violation message
def show_permission_violation():
    st.error("You do not have permission to view this page.")
    st.stop()
