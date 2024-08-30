import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

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
