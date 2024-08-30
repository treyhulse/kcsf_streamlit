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
    '01_Shipping Report.py': ['Sales Manager', 'Administrator'],
    '02_Supply_Chain.py': ['Purchasing Specialist', 'Purchasing Manager', 'Administrator'],
    '03_Marketing.py': ['Marketing', 'Administrator'],
    '03_Sales.py': ['Sales Specialist', 'Sales Manager', 'Administrator'],
    '05_Shop.py': ['Shop Specialist', 'Shop Manager', 'Administrator'],
    '06_Logistics.py': ['Shop Specialist', 'Shop Manager', 'Purchasing Specialist', 'Purchasing Manager', 'Administrator'],
    '07_AI_Insights.py': ['Developer', 'Administrator'],
    '08_Showcase.py': ['Sales Specialist', 'Sales Manager', 'Marketing', 'Administrator'],
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
