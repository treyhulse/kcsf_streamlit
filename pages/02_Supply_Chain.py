import streamlit as st

# Set page config
st.set_page_config(
    page_title="Supply Chain Insights",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
