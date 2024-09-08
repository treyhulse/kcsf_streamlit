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
import pandas as pd
import requests
from requests_oauthlib import OAuth1
import time
import logging
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication setup for all pages
def get_authentication():
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

# SuiteQL Query: JSON Data Handling
def fetch_suiteql_data(query, max_retries=3):
    """Fetch SuiteQL data from NetSuite."""
    url = f"https://{st.secrets['realm']}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    auth = get_authentication()
    all_data = []
    
    payload = {"q": query}
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching SuiteQL data with query: {query}")
            response = requests.post(url, auth=auth, json=payload, headers={"Content-Type": "application/json", "Prefer": "transient"})
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Assuming the response is in JSON format
            data = response.json().get('items', [])

            if not data:
                logger.info("Received empty data. Assuming end of data.")
                return pd.DataFrame(all_data) if all_data else pd.DataFrame()

            all_data.extend(data)
            logger.info(f"Successfully fetched {len(data)} records.")
            return pd.DataFrame(all_data)

        except Exception as e:
            logger.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                st.error(f"Failed to fetch data after {max_retries} attempts.")
                return pd.DataFrame(all_data) if all_data else pd.DataFrame()
            time.sleep(2 ** attempt)  # Exponential backoff

# Streamlit UI for SuiteQL Query
st.title('NetSuite SuiteQL Inventory Query')

# Input for SuiteQL query
item_id = st.text_input('Enter Item ID', value='17842')

query = f"SELECT item, location, quantityonhand, quantityavailable FROM InventoryBalance WHERE item = {item_id}"

if st.button('Fetch Inventory Data'):
    df = fetch_suiteql_data(query)
    
    if not df.empty:
        st.write("Inventory Data:", df)
    else:
        st.error("No data found for the given query.")
