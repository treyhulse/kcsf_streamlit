import streamlit as st

st.set_page_config(page_title="NetSuite Data Analytics", 
                   page_icon="./assets/kcsf_red.png", layout="wide")

st.write("# Welcome to NetSuite Data Analytics! 👋")

st.sidebar.success("Select a report above.")

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