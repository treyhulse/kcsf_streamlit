import streamlit as st
import json
import os

# Initialize empty dictionaries
roles = {}
page_access = {}

# Define the file paths
ROLES_FILE = 'roles.json'
PAGE_ACCESS_FILE = 'page_access.json'

# Function to save roles to a JSON file
def save_roles_to_file():
    with open(ROLES_FILE, 'w') as f:
        json.dump(roles, f, indent=4)

# Function to save page access to a JSON file
def save_page_access_to_file():
    with open(PAGE_ACCESS_FILE, 'w') as f:
        json.dump(page_access, f, indent=4)

# Function to load roles from a JSON file with error handling
def load_roles_from_file():
    global roles
    if os.path.exists(ROLES_FILE):
        try:
            with open(ROLES_FILE, 'r') as f:
                roles = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            st.error("Error loading roles from file. Using default roles.")
            roles = {
                "Administrator": ["trey.hulse@kcstorefixtures.com", "treyhulse3@gmail.com", "gina.bliss@kcstorefixtures.com"],
                "Sales Specialist": ["becky.dean@kcstorefixtures.com", "treyhulse3@kcstorefixtures.com"],
                "Sales Manager": ["anna.alessi@kcstorefixtures.co", "treyhulse3@kcstorefixtures.com"],
                "Financial": ["sean.castle@kcstorefixtures.co", "treyhulse3@kcstorefixtures.com"],
                "Shop Specialist": ["victor@kc-store-fixtures.com", "treyhulse3@kcstorefixtures.com"],
                "Shop Manager": ["tim@kc-store-fixtures.com", "victor@kc-store-fixtures.com"],
                "Purchasing Specialist": ["matt@kc-store-fixtures.co", "treyhulse3@kcstorefixtures.com"],
                "Purchasing Manager": ["mike@kc-store-fixtures.co", "treyhulse3@kcstorefixtures.com"],
                "Marketing": ["robin.falk@kcstorefixtures.com", "treyhulse3@kcstorefixtures.com"]
            }
            save_roles_to_file()

# Function to load page access from a JSON file with error handling
def load_page_access_from_file():
    global page_access
    if os.path.exists(PAGE_ACCESS_FILE):
        try:
            with open(PAGE_ACCESS_FILE, 'r') as f:
                page_access = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            st.error("Error loading page access from file. Using default page access.")
            page_access = {
                "01_Shipping Report.py": ["Administrator", "Sales Specialist", "Sales Manager", "Financial", "Shop Specialist", "Shop Manager", "Purchasing Specialist", "Purchasing Manager", "Marketing"],
                "02_Supply_Chain.py": ["Administrator", "Sales Specialist", "Sales Manager", "Financial", "Shop Specialist", "Shop Manager", "Purchasing Specialist", "Purchasing Manager", "Marketing"],
                "03_Marketing.py": ["Administrator", "Sales Specialist", "Sales Manager", "Financial", "Shop Specialist", "Shop Manager", "Purchasing Specialist", "Purchasing Manager", "Marketing"],
                "03_Sales.py": ["Administrator", "Sales Specialist", "Sales Manager", "Financial", "Shop Specialist", "Shop Manager", "Purchasing Specialist", "Purchasing Manager", "Marketing"],
                "05_Shop.py": ["Administrator", "Sales Specialist", "Sales Manager", "Financial", "Shop Specialist", "Shop Manager", "Purchasing Specialist", "Purchasing Manager", "Marketing"],
                "06_Logistics.py": ["Administrator", "Sales Specialist", "Sales Manager", "Financial", "Shop Specialist", "Shop Manager", "Purchasing Specialist", "Purchasing Manager", "Marketing"],
                "07_AI_Insights.py": ["Administrator", "Sales Specialist", "Sales Manager", "Financial", "Shop Specialist", "Shop Manager", "Purchasing Specialist", "Purchasing Manager", "Marketing", "Developer"],
                "08_Showcase.py": ["Administrator", "Sales Specialist", "Sales Manager", "Financial", "Shop Specialist", "Shop Manager", "Purchasing Specialist", "Purchasing Manager", "Marketing"],
                "09_Role_Permissions.py": ["Administrator"]
            }
            save_page_access_to_file()

# Load roles and page access data when the module is imported
load_roles_from_file()
load_page_access_from_file()

# Function to validate if an email has a specific role
def has_role(email, role):
    return email in roles.get(role, [])

# Function to get all roles of a user by their email
def get_user_roles(email):
    user_roles = []
    for role, emails in roles.items():
        if email in emails:
            user_roles.append(role)
    return user_roles

# Function to capture the user's email using st.experimental_user
def capture_user_email():
    user_info = st.experimental_user
    if user_info is not None:
        return user_info.get('email')
    else:
        return None

# Function to validate if a user can access a specific page
def validate_page_access(email, page_name):
    user_roles = get_user_roles(email)
    allowed_roles = page_access.get(page_name, [])
    return any(role in allowed_roles for role in user_roles)

# Universal permission violation message
def show_permission_violation():
    st.error("You do not have permission to view this page.")
    st.stop()
