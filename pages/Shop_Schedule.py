import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide",)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Shop'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################
import streamlit as st
import pandas as pd
import json  # Import JSON module to ensure proper payload formatting
import altair as alt
from utils.rest import make_netsuite_rest_api_request  # Assuming the correct path is utils/rest.py
from utils.restlet import fetch_restlet_data

# Set the page title
st.title("Shop Schedule")

# Cache the raw data fetching process with a 10-minute expiration
@st.cache_data(ttl=600)
def fetch_raw_data_with_progress(saved_search_id):
    # Initialize progress bar
    progress_bar = st.progress(0)
    
    # Fetch data using the restlet function
    df = fetch_restlet_data(saved_search_id)
    progress_bar.progress(33)  # 33% done after fetching data
    progress_bar.progress(100)  # 100% done
    progress_bar.empty()  # Remove progress bar when done
    return df

# Fetch raw data from the customsearch ID with progress bar
customsearch5163_data_raw = fetch_raw_data_with_progress("customsearch5163")

# Define the dictionaries for status and substatus
work_order_status_dict = {
    1: "In Shop",
    2: "Pending WO",
    3: "Design/Eng.",
    4: "Done",
    5: "On Hold",
    6: "To Be Scheduled",
    9: "Metal Shop"
}

substatus_dict = {
    1: "Cutting/EB",
    2: "Machining",
    3: "Assembly (Stock)",
    4: "Assembly (CF)",
    5: "Packing",
    6: "Done",
    7: "TBD",
    8: "Approval Drawing",
    9: "Pending Customer Approval",
    10: "Shop Drawing",
    11: "CNC Files",
    12: "Cut Sheet",
    13: "Work Order",
    14: "Ready for Shop",
    15: "BOM Drawing"
}

# Function to handle posting updates back to NetSuite using PATCH
def update_work_order_status(internal_id, new_status_id, new_substatus_id):
    update_payload = {
        "custbody34": new_status_id,     # Field ID for work order status
        "custbody178": new_substatus_id  # Field ID for substatus
    }
    
    # Ensure the base URL is correctly prefixed
    base_url = st.secrets["rest_url"]  # The base URL should be stored in your Streamlit secrets
    full_url = f"{base_url}/workOrder/{internal_id}"  # Construct the full URL using the base URL and internal ID

    # Display the payload and URL for debugging purposes
    st.write(f"Payload for Work Order {internal_id}: {update_payload}")
    st.write(f"Full URL: {full_url}")

    try:
        # Send a PATCH request to update the record in NetSuite
        response = make_netsuite_rest_api_request(full_url, update_payload, method="PATCH")
        
        # Debugging: Display response status and content
        if response:
            st.success(f"Successfully updated Work Order ID {internal_id}. Response: {response}")
        else:
            st.error(f"Failed to update Work Order ID {internal_id}. Response: {response}")
    except Exception as e:
        st.error(f"Error in processing the request: {e}")


# Apply custom CSS styling for the card container
st.markdown(
    """
    <style>
    .card {
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
        padding: 16px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the cards for each work order
for index, row in customsearch5163_data_raw.iterrows():
    # Create a card container for each work order with custom styling
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Top row with Status and Substatus
        col1, col2 = st.columns([3, 1])  # Adjusted to have more space for status
        col1.success(f"{row['WO Status']}")  # Display work order status as st.success without the prefix
        col2.info(f"Substatus: {row['Substatus']}")  # Display substatus in info style

        # Display additional work order details below the status and substatus
        st.write(f"**Work Order Number:** {row['Work Order Number']}")
        st.write(f"**Item:** {row['item']}")
        st.write(f"**Customer:** {row['Customer']}")
        st.write(f"**Start Date:** {row['Start Date']}")
        st.write(f"**End Date:** {row['End Date']}")

        # Dropdowns for status and substatus selection with unique keys
        new_status = st.selectbox(
            "Change Work Order Status",
            options=list(work_order_status_dict.values()),
            index=list(work_order_status_dict.values()).index(row['WO Status']) if row['WO Status'] in work_order_status_dict.values() else 0,
            key=f"status_select_{index}"
        )

        new_substatus = st.selectbox(
            "Change Substatus",
            options=list(substatus_dict.values()),
            index=list(substatus_dict.values()).index(row['Substatus']) if row['Substatus'] in substatus_dict.values() else 0,
            key=f"substatus_select_{index}"
        )

        # Progress bar for tracking work order progress (e.g., arbitrary completion percentage)
        st.progress(50)  # Example placeholder for a progress value

        # Button to post back changes to NetSuite with a unique key
        if st.button(f"Update Work Order {row['Work Order Number']}", key=f"update_button_{index}"):
            # Get internal IDs for status and substatus
            new_status_id = next(key for key, value in work_order_status_dict.items() if value == new_status)
            new_substatus_id = next(key for key, value in substatus_dict.items() if value == new_substatus)
            
            # Update work order status
            update_work_order_status(row['Internal ID'], new_status_id, new_substatus_id)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close the card container
