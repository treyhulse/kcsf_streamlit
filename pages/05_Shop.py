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
from dateutil.relativedelta import relativedelta

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

def get_date_range(option):
    today = datetime.today()
    
    if option == "Today":
        start_date = today
        end_date = today
    elif option == "This Week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif option == "This Month":
        start_date = today.replace(day=1)
        end_date = today.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
    elif option == "This Quarter":
        quarter = (today.month - 1) // 3 + 1
        start_date = datetime(today.year, 3 * quarter - 2, 1)
        end_date = (start_date + relativedelta(months=3)) - timedelta(days=1)
    else:
        start_date = today.replace(day=1)
        end_date = today.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
    
    return start_date, end_date

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

def get_sub_status_color(sub_status):
    if sub_status == "Ready for Shop":
        return "#ffc107"  # Yellow
    elif sub_status == "In Progress":
        return "#17a2b8"  # Blue
    elif sub_status == "Completed":
        return "#28a745"  # Green
    else:
        return "#6c757d"  # Grey

def get_progress(sub_status):
    if sub_status == "Ready for Shop":
        return 0.25
    elif sub_status == "In Progress":
        return 0.50
    elif sub_status == "Completed":
        return 1.0
    else:
        return 0.0

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
        font-weight: bold;
        padding: 5px;
        border-radius: 4px;
    }
    </style>
    """
    st.markdown(card_css, unsafe_allow_html=True)

    # Display each work order as a card
    for obj in data:
        progress = get_progress(obj['Sub Status'])
        sub_status_color = get_sub_status_color(obj['Sub Status'])

        st.markdown(
            f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between;">
                    <p class="status">Status: {obj['WO Status']}</p>
                    <p class="sub-status" style="background-color: {sub_status_color};">Sub Status: {obj['Sub Status']}</p>
                </div>
                <progress value="{progress}" max="1.0" style="width: 100%; height: 20px;"></progress>
                <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                    <div>
                        <p><strong>Item:</strong> {obj['Item']}</p>
                        <p><strong>Description:</strong> {obj['Description']}</p>
                        <p><strong>Quantity:</strong> {obj['Qty']}</p>
                        <p><strong>Name:</strong> {obj['Name']}</p>
                    </div>
                    <div>
                        <p><strong>Sales Order #:</strong> {obj['SO#']}</p>
                        <p><strong>Back Order:</strong> {obj['BO']}</p>
                        <p><strong>Start Date:</strong> {obj['Start Date']}</p>
                        <p><strong>Completion Date:</strong> {obj['Completion Date']}</p>
                    </div>
                </div>
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

    date_options = ["Today", "This Week", "This Month", "This Quarter"]
    
    start_date_option = st.sidebar.selectbox("Start Date Range", date_options, index=2)
    completion_date_option = st.sidebar.selectbox("Completion Date Range", date_options, index=2)

    start_date_filter, _ = get_date_range(start_date_option)
    _, end_date_filter = get_date_range(completion_date_option)

    if st.button("Fetch and Display Work Orders"):
        data = get_collection_data(client, collection_name)
        filtered_data = filter_data(data, status_filter, sub_status_filter, start_date_filter, end_date_filter)
        display_object_cards(filtered_data)

if __name__ == "__main__":
    main()
