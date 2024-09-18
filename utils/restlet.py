import requests
import pandas as pd
from requests_oauthlib import OAuth1
import logging
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth1 Authentication setup for NetSuite
def get_authentication():
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

# Function to fetch JSON data from RESTlet and convert it to a DataFrame
def fetch_restlet_data(saved_search_id):
    url = f"{st.secrets['url_restlet']}&savedSearchId={saved_search_id}"
    auth = get_authentication()
    
    try:
        logger.info(f"Fetching data from: {url}")
        response = requests.get(url, auth=auth, headers={"Content-Type": "application/json"})
        response.raise_for_status()

        # Assuming the response is JSON, turn it into a DataFrame
        data = response.json()

        if not data or len(data) == 0:
            logger.info("No data returned.")
            return pd.DataFrame()  # Return empty DataFrame if no data

        # Convert list of dictionaries into a DataFrame
        df = pd.DataFrame(data)
        return df

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()
