import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import pandas as pd
import plotly.express as px

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################
import streamlit as st
import requests
import json
from requests_oauthlib import OAuth1


st.title("Post Data to NetSuite")

# Display a status message
status_placeholder = st.empty()

# Replace these variables with your own secrets
url = "https://3429264.suitetalk.api.netsuite.com/services/rest/record/v1/salesOrder/9318465"
consumer_key = st.secrets["consumer_key"]
consumer_secret = st.secrets["consumer_secret"]
token = st.secrets["token_key"]
token_secret = st.secrets["token_secret"]
realm = st.secrets["realm"]

# Create the request payload
payload = {
    "shippingCost": 50,
    "shipMethod": {
        "id": "36"
    }
}

# Show the payload in Streamlit
st.write("Payload to be sent:", payload)

# Convert payload to JSON
payload_json = json.dumps(payload)

# Create OAuth1 object
auth = OAuth1(
    client_key=consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=token,
    resource_owner_secret=token_secret,
    realm=realm,
    signature_method='HMAC-SHA256'
)

# Headers for the request
headers = {
    'Content-Type': 'application/json',
    'Prefer': 'return-content'
}

# Display button for user to trigger the request
if st.button("Post to NetSuite"):
    try:
        # Make the API request
        response = requests.patch(url, headers=headers, data=payload_json, auth=auth)

        # Display the response
        if response.status_code == 200:
            status_placeholder.success("Data successfully posted to NetSuite!")
            st.write("Response:", response.json())
        else:
            status_placeholder.error(f"Failed to post data to NetSuite. Status Code: {response.status_code}")
            st.write("Response Text:", response.text)

    except Exception as e:
        status_placeholder.error(f"Error occurred: {str(e)}")
