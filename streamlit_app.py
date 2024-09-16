import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(
    page_title="KC Store Fixtures",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

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