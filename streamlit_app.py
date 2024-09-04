import streamlit as st

st.set_page_config(
    page_title="NetSuite Data Analytics",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://kcstorefixtures.streamlit.app/',
        'Report a bug': 'https://www.kc-store-fixtures.com/bug',
        'About': "This is a dashboard and chart management tool."
    }
)

st.write("# Welcome to NetSuite Data Analytics! 👋")

st.sidebar.image("./assets/kcsf_red.png", use_column_width=True)
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