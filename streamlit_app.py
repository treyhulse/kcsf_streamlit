import streamlit as st
from utils.sync_scheduler import setup_sync_scheduler

st.set_page_config(
    page_title="NetSuite Data Analytics",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Start the sync scheduler
scheduler = setup_sync_scheduler()

st.write("# Welcome to NetSuite Data Analytics! 👋")

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