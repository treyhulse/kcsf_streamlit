import streamlit as st
from pymongo import MongoClient
from utils.mongo_connection import get_mongo_client
import ast

# Establish MongoDB connection
client = get_mongo_client()
db = client['netsuite']
roles_collection = db['roles']
permissions_collection = db['permissions']

# Function to get roles for an email
def get_roles_for_email(email):
    roles = roles_collection.find({"emails": {"$regex": f".*{email}.*", "$options": "i"}})
    return [role['role'] for role in roles]

# Function to check if a role has access to a page
def has_access_to_page(page_name, role):
    permission = permissions_collection.find_one({"page": page_name})
    if permission and role in permission['roles']:
        return True
    return False

# Validate access to a page based on the user's roles
def validate_page_access(email, page_name):
    roles = get_roles_for_email(email)
    for role in roles:
        if has_access_to_page(page_name, role):
            return True
    return False

# Capture user email
def capture_user_email():
    user_info = st.experimental_user
    if user_info:
        return user_info.get('email')
    return None

# Show permission violation message
def show_permission_violation():
    st.error("You do not have permission to view this page.")
    st.stop()
