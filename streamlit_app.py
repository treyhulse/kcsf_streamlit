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


# Brief introduction
st.write("""
This is where you can access various modules to manage and analyze different aspects of our company including inventory, sales, order management, reporting, and more.

This app is actively being developed, so things will change periodically. Updates will freshen up the pages, and new features will be added. To recommend new features, please email [trey.hulse@kcstorefixtures.com](mailto:trey.hulse@kcstorefixtures.com) for now.

I'll try to get a digital suggestion box set up or something at some point. Now, see below for tips & tricks.
""")

# Add a Tips & Tricks section
st.header("Tips & Tricks")
st.write("""
- **Navigation**: Use the sidebar on the left to switch between different modulpageses.
- **Filtering**: Utilize the filtering options within each module to view specific data from within the sidebar.
- **Extracting Data**: Download CSVs for any filtered or displayed data for further analysis in the top right of any table.
- **Searching Data**: Use the interactive search mechanism in the top right of tables to find specific order numbers, customers, ship methods, etc.
- **Data Refresh**: Most data in here has a cache mechanism setup where it is refreshed every 15-20 minutes. I can work on adding a refresh button to update the data. The cache is too prevent recurring load times.
- **Regular Updates**: Keep an eye out for new features and improvements to the existing modules. If the app is rebooting, you'll get a white screen with a cake icon in the middle. This reboot takes anywhere from 10 to 60 seconds.
""")

st.info("This is a work in progress, and your feedback is valuable to improve the app. Feel free to reach out!")

