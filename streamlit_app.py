import streamlit as st

# Set the page configuration with title and favicon
st.set_page_config(page_title="NetSuite Data Analytics", 
                   page_icon="./assets/KCSF_Sqaure.png", layout="wide")

# Add the logo to the top of the sidebar
st.sidebar.image("./assets/kcsf_red.png", use_column_width=True)

# Rename the default app title to 'Home'
st.sidebar.header("Home")

# Add a success message below the title in the sidebar
st.sidebar.success("Select a report above.")

# Main content
st.write("# Welcome to NetSuite Data Analytics! 👋")

# Information about the available reports
st.markdown(
    """
    This app provides various reports and analytics for NetSuite data.
    
    👈 Select a report from the sidebar to get started!
    
    ### Available Reports:
    - Shipping Report
    - Sales Dashboard (still working on this!)
    - Supply Chain Insights (still working on this!)
    - Financial Insights (still working on this!)
    - Operations Insights (still working on this!)
    - Logistics Insights (still working on this!)
    - AI Insights (still working on this!)

    More reports coming soon!
    """
)
