"""
KCSF Shipping Report - Main Application

This is the main entry point for the KCSF Shipping Report Streamlit application.
It configures the application settings and sets up navigation to the shipping report page.

Author: KCSF Development Team
"""

import streamlit as st

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="KCSF Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# NAVIGATION SETUP
# =============================================================================

# Define available pages
pages = [
    st.Page("pages/Home.py", title="Home"),
    st.Page("pages/Shipping_Report.py", title="Shipping Report"),
]

# Create navigation and run the selected page
pg = st.navigation(pages)
pg.run()
