import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '05_Shop.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import logging
from pymongo import MongoClient
import streamlit as st
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    filename="netsuite_page.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

# Use st.cache_resource to cache the MongoDB client
@st.cache_resource
def get_mongo_client():
    try:
        logging.debug("Attempting to connect to MongoDB...")
        connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
        client = MongoClient(connection_string, 
                             ssl=True,
                             serverSelectionTimeoutMS=30000,
                             connectTimeoutMS=30000,
                             socketTimeoutMS=30000)
        logging.info("MongoDB connection successful")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise

# Function to fetch and process data from MongoDB
def get_collection_data(client, collection_name):
    try:
        logging.debug(f"Fetching data from collection: {collection_name}")
        db = client['netsuite']  # Ensure the database name is correct
        collection = db[collection_name]
        
        data = []
        for doc in collection.find():
            try:
                # Process each document into a dictionary
                obj = {
                    "Internal ID": doc.get("Internal ID"),
                    "WO #": doc.get("WO #"),
                    "Item": doc.get("Item"),
                    "Description": doc.get("Description (Display Name)"),
                    "Qty": doc.get("Qty"),
                    "Name": doc.get("Name"),
                    "SO#": doc.get("SO#"),
                    "BO": doc.get("BO"),
                    "WO Status": doc.get("WO Status"),
                    "Sub Status": doc.get("Sub Status"),
                    "Start Date": doc.get("Start Date"),
                    "Completion Date": doc.get("Completion Date"),
                    "Ship Via": doc.get("Ship Via"),
                    "*Here?": doc.get("*Here?")
                }
                data.append(obj)
                
            except Exception as e:
                logging.error(f"Skipping problematic document {doc.get('_id', 'Unknown ID')}: {e}")
                continue  # Skip problematic document
        
        logging.info(f"Data fetched successfully from {collection_name} with {len(data)} records.")
        return data
    except Exception as e:
        logging.error(f"Error fetching data from collection {collection_name}: {e}")
        raise

def filter_data(data, status_filter, sub_status_filter, start_date_filter, end_date_filter):
    filtered_data = []

    for obj in data:
        start_date = datetime.strptime(obj.get("Start Date"), "%m/%d/%Y")
        end_date = datetime.strptime(obj.get("Completion Date"), "%m/%d/%Y")

        if (status_filter == 'All' or obj.get("WO Status") == status_filter) and \
           (sub_status_filter == 'All' or obj.get("Sub Status") == sub_status_filter) and \
           (start_date_filter <= start_date <= end_date_filter) and \
           (start_date_filter <= end_date <= end_date_filter):
            filtered_data.append(obj)

    return filtered_data

def display_object_cards(data):
    st.write("### Work Order Progress")
    
    # Define styles for the cards
    card_css = """
    <style>
    .card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .card h4 {
        margin-top: 0;
    }
    .card p {
        margin: 5px 0;
    }
    .card .status {
        font-weight: bold;
        color: #28a745;  /* Green for success */
    }
    .card .sub-status {
        color: #ffc107;  /* Yellow for warning */
    }
    </style>
    """
    st.markdown(card_css, unsafe_allow_html=True)

    # Display each work order as a card
    for obj in data:
        st.markdown(
            f"""
            <div class="card">
                <h4>Work Order #{obj['WO #']}</h4>
                <p><strong>Item:</strong> {obj['Item']}</p>
                <p><strong>Description:</strong> {obj['Description']}</p>
                <p><strong>Quantity:</strong> {obj['Qty']}</p>
                <p><strong>Name:</strong> {obj['Name']}</p>
                <p><strong>Sales Order #:</strong> {obj['SO#']}</p>
                <p><strong>Back Order:</strong> {obj['BO']}</p>
                <p class="status"><strong>Status:</strong> {obj['WO Status']}</p>
                <p class="sub-status"><strong>Sub Status:</strong> {obj['Sub Status']}</p>
                <p><strong>Start Date:</strong> {obj['Start Date']}</p>
                <p><strong>Completion Date:</strong> {obj['Completion Date']}</p>
                <p><strong>Ship Via:</strong> {obj['Ship Via']}</p>
                <p><strong>*Here?:</strong> {obj['*Here?']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Streamlit page layout
def main():
    st.title("NetSuite Work Orders Progress")

    client = get_mongo_client()
    collection_name = "workOrders"

    # Sidebar filters
    status_options = ["All", "Metal Shop", "Painting", "Assembly"]
    sub_status_options = ["All", "Ready for Shop", "In Progress", "Completed"]

    st.sidebar.header("Filters")

    status_filter = st.sidebar.selectbox("Status", status_options, index=0)
    sub_status_filter = st.sidebar.selectbox("Sub Status", sub_status_options, index=0)

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Start of the current week
    end_of_week = start_of_week + timedelta(days=6)  # End of the current week

    start_date_filter = st.sidebar.date_input("Start Date", value=start_of_week)
    end_date_filter = st.sidebar.date_input("Completion Date", value=end_of_week)

    if st.button("Fetch and Display Work Orders"):
        data = get_collection_data(client, collection_name)
        filtered_data = filter_data(data, status_filter, sub_status_filter, start_date_filter, end_date_filter)
        display_object_cards(filtered_data)

if __name__ == "__main__":
    main()
