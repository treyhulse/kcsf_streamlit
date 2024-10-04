import streamlit as st
import pandas as pd
from datetime import date
from utils.mongo_connection import get_mongo_client, get_collection_data

# Set page configuration with collapsed sidebar
st.set_page_config(
    page_title="KC Store Fixtures",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
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
st.title(f"Welcome to our KC Store Fixtures App! 👋")
st.subheader(f"**Today's Date:** {today.strftime('%B %d, %Y')}")

# Brief introduction
st.write("""
This app is actively being developed so new features will be added periodically. 

To recommend new features, please email [trey.hulse@kcstorefixtures.com](mailto:trey.hulse@kcstorefixtures.com) for now. I'll try to get a digital suggestion box set up at some point. 

""")

# Add a Tips & Tricks section
st.header("Tips & Tricks")
st.write("""
- **How To Access the Shipping Report**: Navigate to the shipping report page. In here, change the **Ship Date** selection to **"Past (including today)"** to view all orders with a ship date on or before today. You can filter to just your name as well if you are a sales rep. To see orders, open the **expandable table** at the bottom of the page. This is what would be exported and sent to you.
- **Navigation**: Use the sidebar on the left to switch between different pages. Strongly recommend bookmarking frequently visited pages.
- **Filtering**: Utilize the filtering options within the sidebar to view specific data. (I'm working on a pre-filter so that when you view a page, it defaults to being filtered to just you.)
- **Extracting Data**: You can download CSVs from any table for further use with the download icon in the top right of any table. You can also capture visualizations as images. Explore that as you wish.
- **Searching Data**: Use the interactive search mechanism in the top right of any table to find specific order numbers, customers, ship methods, etc. Anything in the table should be searchable, let me know if it's not.
- **Data Refresh**: Most data in here has a cache mechanism setup where it is refreshes every 15-20 minutes. I can work on adding a refresh button to update the data as needed. The cache is too prevent recurring load times.
- **Regular Updates**: Keep an eye out for new features and improvements to the existing pages. If the app is rebooting, you'll get a white screen with a cake icon in the middle. This reboot takes anywhere from 10 seconds to 60 seconds.
""")

st.info("This is in development and your feedback is valuable to improve the app. Please reach out!")

# Function to map status to color
def get_status_style(status):
    color_map = {
        "Submitted": "#ffcc00",
        "In Consideration": "#66ccff",
        "Building": "#3399ff",
        "Implementing": "#33cc33",
        "Complete": "#66cc66"
    }
    return color_map.get(status, "#999999")  # Default color if status is not found

# Function to create HTML for feature cards
def feature_card(title, description, owner, status):
    color = get_status_style(status)
    card_html = f"""
        <div style='background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin: 15px 0; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);'>
            <h3 style='margin: 0;'>{title}</h3>
            <p style='font-size: 14px;'>{description}</p>
            <p><strong>Owner:</strong> {owner}</p>
            <p><strong>Status:</strong> <span style='color: {color}; font-weight: bold;'>{status}</span></p>
        </div>
    """
    return card_html

# Fetch data from the 'features' collection
try:
    # Initialize the MongoDB client
    mongo_client = get_mongo_client()
    
    # Fetch the 'features' collection data
    features_data = get_collection_data(mongo_client, 'features')

    # Display the features in card format
    if not features_data.empty:
        st.header("Features Under Consideration")
        st.write("Here are the current feature requests and their status:")

        # Generate cards for each feature
        for _, feature in features_data.iterrows():
            st.markdown(feature_card(feature["Title"], feature["Description"], feature["Owner"], feature["Status"]), unsafe_allow_html=True)
    else:
        st.warning("No features found in the 'features' collection.")
except Exception as e:
    st.error(f"Failed to retrieve features data: {e}")
