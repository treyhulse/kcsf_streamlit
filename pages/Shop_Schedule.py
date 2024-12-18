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

import pandas as pd
import json
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

# Sidebar filters for Work Order Status and Substatus
with st.sidebar:
    selected_status = st.multiselect("Filter by Work Order Status", options=list(work_order_status_dict.values()))
    selected_substatus = st.multiselect("Filter by Substatus", options=list(substatus_dict.values()))

# Apply filters to the dataframe
# Start by assuming no filters are applied
filtered_data = customsearch5163_data_raw

# Apply status filter if any status is selected
if selected_status:
    if "WO Status" in customsearch5163_data_raw.columns:
        filtered_data = filtered_data[filtered_data["WO Status"].isin(selected_status)]

# Apply substatus filter if any substatus is selected
if selected_substatus:
    if "Substatus" in customsearch5163_data_raw.columns:
        filtered_data = filtered_data[filtered_data["Substatus"].isin(selected_substatus)]

# Set up pagination variables
PAGE_SIZE = 10  # Number of records to show per page
total_records = len(filtered_data)  # Get total number of records after filtering
total_pages = (total_records - 1) // PAGE_SIZE + 1  # Calculate total number of pages

# Sidebar navigation for pagination
current_page = st.sidebar.number_input("Select page:", min_value=1, max_value=total_pages, value=1, step=1)
start_index = (current_page - 1) * PAGE_SIZE
end_index = start_index + PAGE_SIZE

# Display the current page and total pages information
st.sidebar.write(f"Page {current_page} of {total_pages}")

# Apply pagination to the filtered data
paginated_data = filtered_data.iloc[start_index:end_index]

# Function to handle posting updates back to NetSuite using PATCH
def update_work_order_status(internal_id, new_status_id, new_substatus_id):
    update_payload = {
        "custbody34": new_status_id,     # Field ID for work order status
        "custbody178": new_substatus_id  # Field ID for substatus
    }

    base_url = st.secrets["rest_url"]
    full_url = f"{base_url}workOrder/{internal_id}"

    try:
        # Send a PATCH request to update the record in NetSuite (no return value needed)
        make_netsuite_rest_api_request(full_url, update_payload, method="PATCH")
        
        # If no exception was raised, show a success message
        st.success(f"Successfully updated Work Order ID {internal_id}.")
    except Exception as e:
        # If an exception was raised, show an error message
        st.error(f"Failed to update Work Order ID {internal_id}. Error: {e}")

# Display the paginated work orders as cards
for index, row in paginated_data.iterrows():
    # Create a card container for each work order with custom styling
    with st.container():
        st.write("") # Add an empty line for spacing
        st.divider()  # Add a divider between cards
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
