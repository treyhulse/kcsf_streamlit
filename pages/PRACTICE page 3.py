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
import time
import hmac
import hashlib
import base64
import urllib.parse

# Define the page configuration
st.set_page_config(page_title="NetSuite API POST", page_icon="💼")

# Create Streamlit page
st.title("Post Data to NetSuite")

# Display a status message
status_placeholder = st.empty()

# Function to generate OAuth1.0 headers for the request
def generate_oauth_header(url, method, consumer_key, consumer_secret, token, token_secret):
    oauth_nonce = base64.b64encode(bytes(str(time.time()), 'utf-8')).decode('utf-8')
    oauth_timestamp = str(int(time.time()))
    base_url = urllib.parse.urlparse(url).scheme + "://" + urllib.parse.urlparse(url).hostname

    # Create the signature base string
    signature_base_string = f"{method}&{urllib.parse.quote_plus(url)}"
    signature_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_token": token,
        "oauth_signature_method": "HMAC-SHA256",
        "oauth_timestamp": oauth_timestamp,
        "oauth_nonce": oauth_nonce,
        "oauth_version": "1.0"
    }
    signature_base_string += "&" + urllib.parse.quote_plus('&'.join([f"{k}={v}" for k, v in sorted(signature_params.items())]))

    # Create the signing key
    signing_key = f"{consumer_secret}&{token_secret}"

    # Create the signature
    hashed = hmac.new(bytes(signing_key, 'latin-1'), bytes(signature_base_string, 'latin-1'), hashlib.sha256)
    oauth_signature = base64.b64encode(hashed.digest()).decode()

    # Create the OAuth header
    oauth_header = (
        f'OAuth realm="{base_url}",'
        f'oauth_consumer_key="{consumer_key}",'
        f'oauth_token="{token}",'
        f'oauth_signature_method="HMAC-SHA256",'
        f'oauth_timestamp="{oauth_timestamp}",'
        f'oauth_nonce="{oauth_nonce}",'
        f'oauth_version="1.0",'
        f'oauth_signature="{urllib.parse.quote_plus(oauth_signature)}"'
    )
    return oauth_header

# Replace these variables with your own secrets
url = "https://3429264.suitetalk.api.netsuite.com/services/rest/record/v1/salesOrder/9318465"
consumer_key = st.secrets["consumer_key"]
consumer_secret = st.secrets["consumer_secret"]
token = st.secrets["token_key"]
token_secret = st.secrets["token_secret"]

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

# Generate OAuth header
oauth_header = generate_oauth_header(url, "PATCH", consumer_key, consumer_secret, token, token_secret)

# Headers for the request
headers = {
    'Content-Type': 'application/json',
    'Prefer': 'return-content',
    'Authorization': oauth_header
}

# Display button for user to trigger the request
if st.button("Post to NetSuite"):
    try:
        # Make the API request
        response = requests.patch(url, headers=headers, data=payload_json)

        # Display the response
        if response.status_code == 200:
            status_placeholder.success("Data successfully posted to NetSuite!")
            st.write("Response:", response.json())
        else:
            status_placeholder.error(f"Failed to post data to NetSuite. Status Code: {response.status_code}")
            st.write("Response Text:", response.text)

    except Exception as e:
        status_placeholder.error(f"Error occurred: {str(e)}")
