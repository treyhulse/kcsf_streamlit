import streamlit as st
import pandas as pd
from datetime import date
from utils.mongo_connection import get_mongo_client, get_collection_data

# Set page configuration
st.set_page_config(
    page_title="KC Store Fixtures",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Get today's date
today = date.today()

# MongoDB client setup
client = get_mongo_client()

# Fetch announcements from the 'announcements' collection
announcements_data = get_collection_data(client, 'announcements')

# Welcome message and date
st.write(f"# Welcome to KC Store Fixtures! 👋")
st.write(f"**Today's Date:** {today.strftime('%B %d, %Y')}")

# Announcements section
st.write("### Announcements")
if not announcements_data.empty:
    for index, row in announcements_data.iterrows():
        st.write(f"- {row['announcement']}")
else:
    st.write("No announcements at this time.")

# Sidebar content
st.sidebar.image("./assets/kcsf_red.png", use_column_width=True)
st.sidebar.success("Select a report above.")

# Main content
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
