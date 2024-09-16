import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(
    page_title="KC Store Fixtures",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Shipping Report'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

st.write("# Welcome to KC Store Fixtures! 👋")

st.sidebar.image("./assets/kcsf_red.png", use_column_width=True)
st.sidebar.success("Select a report above.")

st.markdown(
    """
    This app provides various reports and analytics for NetSuite data.
    
    👈 Select a report from the sidebar to get started!
    
    ### Available Reports:
    - Shipping Report
    - Sales Dashboard
    - Supply Chain Insights
    - Financial Insights
    - Operations Insights
    - Logistics Insights
    - AI Insights
    - NetSuite Sync Management

    More reports coming soon!
    """
)

# The rest of your existing streamlit_app.py code...