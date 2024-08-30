import streamlit as st
from utils.auth import capture_user_email, validate_access, show_permission_violation, get_sidebar_content, get_user_role

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Define roles that can access this page
allowed_roles = ['Sales Manager', 'Administrator']
# Optionally, define roles that cannot access this page
# denied_roles = ['Sales Specialist']

# Validate access
if not validate_access(user_email, allowed_roles=allowed_roles):
    show_permission_violation()

# Sidebar content based on role
user_role = get_user_role(user_email)
st.sidebar.title(f"{user_role} Tools")
sidebar_content = get_sidebar_content(user_role)

for item in sidebar_content:
    st.sidebar.write(item)

# Page content
st.title(f"{user_role} Dashboard")
st.write(f"Welcome, {user_email}!")
st.write(f"You have access to the {user_role} tools.")


################################################################################################

## AUTHENTICATED

################################################################################################

# Set page config
st.set_page_config(
    page_title="Supply Chain Insights",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Page title and description
st.title("Supply Chain Insights")
st.write("""
Welcome to the Supply Chain Insights page. Here, you'll find valuable data and metrics to help you manage and optimize 
your supply chain operations, from inventory management to demand forecasting.
""")

# Sidebar configuration
st.sidebar.header("Supply Chain Options")
st.sidebar.write("Use the options below to navigate through supply chain data and analytics.")

# Add any initial content or widgets here
st.subheader("Overview")
st.write("Select options from the sidebar to dive deeper into specific areas of your supply chain.")
