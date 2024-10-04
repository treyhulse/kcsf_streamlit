import streamlit as st
import pandas as pd
from datetime import date
from utils.mongo_connection import get_mongo_client, get_collection_data
from bson.objectid import ObjectId
from utils.auth import capture_user_email

# Set page configuration with collapsed sidebar
st.set_page_config(
    page_title="KC Store Fixtures",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
)

# Custom CSS for card styling
card_style = """
    <style>
    .card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        height: 260px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
        font-size: 14px;
        font-weight: bold;
        color: gray;
    }
    .status {
        font-size: 14px;
        font-weight: bold;
        text-align: center;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .status-submitted { background-color: #ffcccc; color: #cc0000; }
    .status-in-consideration { background-color: #cce5ff; color: #007bff; }
    .status-building { background-color: #cce5ff; color: #007bff; }
    .status-implementing { background-color: #ccffcc; color: #28a745; }
    .status-complete { background-color: #d4edda; color: #155724; }
    </style>
"""
st.markdown(card_style, unsafe_allow_html=True)

# Get today's date
today = date.today()

# Welcome message and date
st.title(f"Welcome to our KC Store Fixtures App! 👋")
st.subheader(f"**Today's Date:** {today.strftime('%B %d, %Y')}")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Admin email list
admin_email = "trey.hulse@kcstorefixtures.com"



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

# Function to map status to custom CSS class for styling
def get_status_class(status):
    status_class = {
        "Submitted": "status-submitted",
        "In Consideration": "status-in-consideration",
        "Building": "status-building",
        "Implementing": "status-implementing",
        "Complete": "status-complete"
    }
    return status_class.get(status, "status-unknown")

# Function to update feature status in the database
def update_feature_status(feature_id, new_status):
    try:
        client = get_mongo_client()
        db = client['netsuite']
        features_collection = db['features']
        # Update the feature status
        features_collection.update_one(
            {"_id": ObjectId(feature_id)},
            {"$set": {"Status": new_status}}
        )
        st.success("Feature status updated successfully!")
    except Exception as e:
        st.error(f"Failed to update feature status: {e}")

# Updated feature_card function to debug and print feature IDs
def feature_card(feature_id, title, description, owner, status):
    status_class = get_status_class(status)
    
    # Debugging print to check feature ID and other details
    print(f"Feature ID: {feature_id}, Title: {title}")

    # Display the feature card
    card_html = f"""
        <div class='card'>
            <div class='card-header'>{title}</div>
            <div class='card-body'>{description}</div>
            <div class='status {status_class}'>{status}</div>
            <div class='card-footer'>Owner: {owner}</div>
        </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    # If the user is an admin, provide a dropdown to update the feature status
    if user_email == admin_email:
        new_status = st.selectbox(
            f"Update status for '{title}' (ID: {feature_id}):",
            options=["Submitted", "In Consideration", "Building", "Implementing", "Complete"],
            index=["Submitted", "In Consideration", "Building", "Implementing", "Complete"].index(status)
        )
        if st.button(f"Update Status for '{title}'"):
            update_feature_status(feature_id, new_status)

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

# Display Add New Feature form as the top card
st.header("New Feature Requests")
st.markdown("#### Add New Feature")
new_title = st.text_input("Feature Title", "")
new_description = st.text_area("Feature Description", "")
submit_button = st.button("Submit Feature")

if submit_button and new_title and new_description:
    # Add feature to the database
    add_feature_to_db(new_title, new_description, user_email)

# Updated main code block to capture and print feature IDs
try:
    # Initialize the MongoDB client
    mongo_client = get_mongo_client()
    
    # Fetch the 'features' collection data and ensure `_id` is converted to string
    features_data = get_collection_data(mongo_client, 'features')

    # Display the features in 4 columns layout
    if not features_data.empty:
        # Create four columns for the feature cards
        col1, col2, col3, col4 = st.columns(4)

        columns = [col1, col2, col3, col4]
        column_index = 0

        # Iterate over each feature and display in a card
        for _, feature in features_data.iterrows():
            feature_id = feature["_id"]  # Ensure this is a string type
            print(f"Feature ID (string format): {feature_id}")  # Debug print
            
            with columns[column_index]:
                feature_card(
                    feature_id=feature_id,  # Pass feature ID as string
                    title=feature["Title"],
                    description=feature["Description"],
                    owner=feature["Owner"],
                    status=feature["Status"]
                )
            column_index = (column_index + 1) % 4  # Cycle through the four columns
    else:
        st.warning("No features found in the 'features' collection.")
except Exception as e:
    st.error(f"Failed to retrieve features data: {e}")