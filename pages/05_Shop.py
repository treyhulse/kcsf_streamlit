import streamlit as st
from utils.auth import has_role, has_any_role, get_user_role
from auth import capture_user_email, validate_access, show_permission_violation, get_sidebar_content


# Capture the user's email dynamically
user_info = st.experimental_user
if user_info is not None:
    user_email = user_info['email']
else:
    st.error("Unable to retrieve user information.")
    st.stop()

# Check the user's role and grant access accordingly
user_role = get_user_role(user_email)

if user_role is None:
    st.error("You do not have permission to view this page.")
    st.stop()

st.sidebar.title("Navigation")

if has_role(user_email, 'Director'):
    st.sidebar.header("Director Tools")
    st.sidebar.write("Access to high-level analytics.")
elif has_role(user_email, 'Manager'):
    st.sidebar.header("Manager Tools")
    st.sidebar.write("Manage your team's performance.")
elif has_role(user_email, 'Person'):
    st.sidebar.header("Employee Tools")
    st.sidebar.write("View your tasks and progress.")
else:
    st.sidebar.write("Limited Access")

# Page content based on role
st.title(f"{user_role} Dashboard")
st.write(f"Welcome, {user_email}!")
st.write(f"You have access to the {user_role} dashboard.")

# Add role-specific content here
if has_role(user_email, 'Director'):
    st.write("This is sensitive Director-level content.")
elif has_role(user_email, 'Manager'):
    st.write("This is Manager-level content.")
elif has_role(user_email, 'Person'):
    st.write("This is general Employee content.")
