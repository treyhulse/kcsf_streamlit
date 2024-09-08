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
from requests_oauthlib import OAuth1

# Accessing secrets securely from st.secrets
CONSUMER_KEY = st.secrets["consumer_key"]
CONSUMER_SECRET = st.secrets["consumer_secret"]
TOKEN_KEY = st.secrets["token_key"]
TOKEN_SECRET = st.secrets["token_secret"]
REALM = st.secrets["realm"]

# OAuth 1.0 setup
oauth = OAuth1(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=TOKEN_KEY,
    resource_owner_secret=TOKEN_SECRET,
    signature_method='HMAC-SHA256'
)

# Function to query NetSuite SuiteQL
def query_netsuite(item_id):
    url = f"https://{REALM}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    headers = {"Content-Type": "application/json", "Prefer": "transient"}
    query = {
        "q": f"SELECT item, location, quantityonhand, quantityavailable FROM InventoryBalance WHERE item = {item_id}"
    }
    response = requests.post(url, headers=headers, json=query, auth=oauth)

    if response.status_code == 200:
        return response.json()  # Returns the JSON response
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# Streamlit App UI
st.title('NetSuite Inventory Query')

# Input for item ID
item_id = st.text_input('Enter Item ID', value='17842')

if st.button('Fetch Inventory Data'):
    data = query_netsuite(item_id)
    
    if data:
        # Display data in a table
        st.write("Inventory Data:", data)
        for row in data['items']:
            st.write(f"Item: {row['item']}, Location: {row['location']}, Quantity On Hand: {row['quantityonhand']}, Quantity Available: {row['quantityavailable']}")
