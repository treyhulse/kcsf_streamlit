import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

from streamlit_echarts import st_echarts

# Sample data for testing
chart_data = [
    {"value": 1048, "name": "Tasked Orders"},
    {"value": 735, "name": "Untasked Orders"}
]

# Simplified pie chart options
options = {
    "series": [
        {
            "type": "pie",
            "radius": "50%",
            "data": chart_data
        }
    ]
}

# Test rendering the chart
st_echarts(options=options, height="500px")
