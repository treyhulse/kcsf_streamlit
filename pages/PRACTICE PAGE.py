import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################
import streamlit as st
import requests
import time
from requests_oauthlib import OAuth1

# Accessing secrets securely from st.secrets
CONSUMER_KEY = st.secrets["consumer_key"]
CONSUMER_SECRET = st.secrets["consumer_secret"]
TOKEN_KEY = st.secrets["token_key"]
TOKEN_SECRET = st.secrets["token_secret"]
REALM = st.secrets["realm"]

# Display Streamlit UI
st.title('NetSuite Inventory Query')

# Input for item ID
item_id = st.text_input('Enter Item ID', value='17842')

# Debugging - show OAuth timestamp and nonce generation (time is dynamic)
st.write(f"OAuth Timestamp: {int(time.time())}")

if st.button('Fetch Inventory Data'):
    # OPTION 1: Manually Use the Headers from Postman
    headers = {
        'Prefer': 'transient',
        'Content-Type': 'application/json',  # You can try 'text/plain' if Postman used that
        # Copy the exact Authorization header from Postman for troubleshooting
        'Authorization': 'OAuth realm="3429264",oauth_consumer_key="your_consumer_key",oauth_token="your_token_key",oauth_signature_method="HMAC-SHA256",oauth_timestamp="your_timestamp",oauth_nonce="your_nonce",oauth_version="1.0",oauth_signature="your_signature"'
    }

    # Payload (query for SuiteQL)
    query = {
        "q": f"SELECT item, location, quantityonhand, quantityavailable FROM InventoryBalance WHERE item = {item_id}"
    }

    # Make the POST request using copied Postman headers
    url = f"https://{REALM}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    response = requests.post(url, headers=headers, json=query)

    # Output the response in Streamlit
    if response.status_code == 200:
        st.write(response.json())  # Display the returned data in JSON format
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        st.write("Response Headers: ", response.headers)

    # OPTION 2: Using dynamic OAuth signature generation
    oauth = OAuth1(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=TOKEN_KEY,
        resource_owner_secret=TOKEN_SECRET,
        signature_method='HMAC-SHA256'
    )

    # If you want to fall back to the dynamically generated OAuth1 signature instead
    response_dynamic = requests.post(url, headers={"Content-Type": "application/json", "Prefer": "transient"}, json=query, auth=oauth)

    # Output the dynamic request result in Streamlit (if manually copying headers fails)
    if response_dynamic.status_code == 200:
        st.write(response_dynamic.json())
    else:
        st.error(f"Dynamic OAuth Error: {response_dynamic.status_code} - {response_dynamic.text}")
        st.write("Dynamic Response Headers: ", response_dynamic.headers)
