import streamlit as st
from st_pages import Page, show_pages, add_page_title

# Set the page configuration with title and favicon
st.set_page_config(page_title="NetSuite Data Analytics", 
                   page_icon="./assets/KCSF_Sqaure.png", layout="wide")

# Add the title and icon to the current page
add_page_title()

# Add the logo to the top of the sidebar
st.sidebar.image("./assets/kcsf_red.png", use_column_width=True)

# Specify what pages should be shown in the sidebar, and their titles and icons
show_pages(
    [
        Page("streamlit_app.py", "Home", "🏠"),
        Page("other_pages/page2.py", "Shipping Report", "📦"),
        Page("other_pages/page3.py", "Supply Chain", "🔗"),
        Page("other_pages/page4.py", "Marketing", "📈"),
        Page("other_pages/page5.py", "Sales", "💼"),
        Page("other_pages/page6.py", "Shop", "🏭"),
        Page("other_pages/page7.py", "Logistics", "🚚"),
        Page("other_pages/page8.py", "AI Insights", "🤖"),
        Page("other_pages/page9.py", "Showcase", "🌟"),
        Page("other_pages/page10.py", "Role Permissions", "🔒"),
    ]
)

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
