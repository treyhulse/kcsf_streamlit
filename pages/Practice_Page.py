import streamlit as st
import pandas as pd
from datetime import date
from utils.mongo_connection import get_mongo_client, get_collection_data
from bson.objectid import ObjectId

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

# Additional CSS for card styling
card_style = """
    <style>
    .card {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        margin: 15px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }
    .card-header {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .card-body {
        font-size: 14px;
        margin-bottom: 10px;
    }
    .card-footer {
        font-size: 12px;
        color: gray;
    }
    </style>
"""
st.markdown(card_style, unsafe_allow_html=True)

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

# Function to map status to Streamlit status indicators
def get_status_style(status):
    if status == "Submitted":
        return st.error, "Submitted"
    elif status in ["In Consideration", "Building"]:
        return st.info, status
    elif status in ["Implementing", "Complete"]:
        return st.success, status
    else:
        return st.warning, "Unknown Status"

# Function to create HTML for feature cards using custom styling and Streamlit status
def feature_card(title, description, owner, status):
    status_func, status_label = get_status_style(status)
    with st.container():
        st.markdown(
            f"""
            <div class='card'>
                <div class='card-header'>{title}</div>
                <div class='card-body'>{description}</div>
                <div class='card-footer'>Owner: {owner}<br>Status: {status_label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Show the status indicator
        status_func(status_label)

# Function to add a new feature to the database
def add_feature_to_db(title, description, owner):
    try:
        client = get_mongo_client()
        db = client['netsuite']
        features_collection = db['features']
        
        new_feature = {
            "Title": title,
            "Description": description,
            "Owner": owner,
            "Status": "Submitted",
            "Timestamp": pd.Timestamp.now()
        }
        
        features_collection.insert_one(new_feature)
        st.success("Feature request submitted successfully!")
    except Exception as e:
        st.error(f"Failed to submit feature: {e}")

# Display Add New Feature form as the first card
st.subheader("Feature Request Board")

# Create the first row with the "Add New Feature" card in the first column
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Add New Feature")
    new_title = st.text_input("Feature Title", "")
    new_description = st.text_area("Feature Description", "")
    submit_button = st.button("Submit Feature")
    
    if submit_button and new_title and new_description:
        # Retrieve user email from Streamlit (if authenticated)
        # Here assuming Streamlit's user email is available in st.session_state["user_email"]
        user_email = st.session_state.get("user_email", "anonymous@kcstorefixtures.com")
        
        # Add feature to the database
        add_feature_to_db(new_title, new_description, user_email)

# Fetch and display features from the 'features' collection
try:
    # Initialize the MongoDB client
    mongo_client = get_mongo_client()
    
    # Fetch the 'features' collection data
    features_data = get_collection_data(mongo_client, 'features')

    # Display the features in 3 columns layout
    if not features_data.empty:
        # Counter to track feature placement in columns
        columns = [col2, col3]
        column_index = 0

        # Iterate over each feature and display in a card
        for _, feature in features_data.iterrows():
            with columns[column_index]:
                feature_card(feature["Title"], feature["Description"], feature["Owner"], feature["Status"])
            column_index = (column_index + 1) % 2  # Cycle through col2 and col3
    else:
        st.warning("No features found in the 'features' collection.")
except Exception as e:
    st.error(f"Failed to retrieve features data: {e}")
