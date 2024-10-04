import streamlit as st
import pandas as pd
from datetime import date
from utils.mongo_connection import get_mongo_client, get_collection_data

# Set page configuration with collapsed sidebar
st.set_page_config(
    page_title="KC Store Fixtures",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Get today's date
today = date.today()

# Welcome message and date
st.write(f"# Welcome to our KC Store Fixtures App! 👋")
st.write(f"**Today's Date:** {today.strftime('%B %d, %Y')}")


# Set the title of the homepage
st.title("Welcome to the KC Store Fixtures App")

# Brief introduction
st.write("""
This is where you can access various modules to manage and analyze different aspects of your business, such as inventory, sales, order management, marketing, and more.

This app is actively being developed, so things will change periodically. Updates will refresh the pages, and new features will be added. To recommend new features, please email [trey.hulse@kcstorefixtures.com](mailto:trey.hulse@kcstorefixtures.com) for now.

I'll try to get a suggestion box set up or something at some point. But for now, see below for tips & tricks.
""")

# Add a Tips & Tricks section
st.header("Tips & Tricks")
st.write("""
- **Navigation**: Use the sidebar on the left to switch between different modules.
- **Filtering Data**: Utilize the filtering options within each module to view specific data points.
- **Exporting Data**: Download CSVs for any filtered or displayed data for further analysis.
- **Regular Updates**: Keep an eye out for new features and improvements to the existing modules.
""")

st.info("This is a work in progress, and your feedback is valuable to improve the app. Feel free to reach out!")

