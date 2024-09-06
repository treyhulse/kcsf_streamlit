import streamlit as st
import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
from typing import Dict, Any
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_netsuite_auth():
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

def fetch_data(url: str, page: int = 1) -> Dict[str, Any]:
    """Fetch data from a NetSuite RESTlet endpoint."""
    auth = get_netsuite_auth()
    full_url = f"{url}&page={page}"
    logger.debug(f"Fetching data from URL: {full_url}")
    response = requests.get(full_url, auth=auth)
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")
    response.raise_for_status()
    return response.json()

def process_netsuite_data(url: str) -> pd.DataFrame:
    """Fetch and process NetSuite data."""
    all_data = []
    page = 1
    while True:
        try:
            data = fetch_data(url, page)
            logger.debug(f"Received data: {json.dumps(data, indent=2)}")
            if 'results' not in data or not data['results']:
                logger.warning(f"No results found on page {page}")
                break
            all_data.extend(data['results'])
            if not data.get('hasMore', False):
                break
            page += 1
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data on page {page}: {str(e)}")
            break
    
    if not all_data:
        logger.error("No data retrieved from NetSuite")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    logger.info(f"Retrieved {len(df)} records from NetSuite")
    return df

def load_csv(file):
    """Load data from a CSV file."""
    return pd.read_csv(file)

def main():
    st.title("NetSuite Open Sales Orders")

    # Option to upload CSV for testing
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = load_csv(uploaded_file)
        st.success(f"Data loaded from CSV. {len(df)} records found.")
        st.dataframe(df)
    else:
        try:
            with st.spinner("Fetching data from NetSuite..."):
                df = process_netsuite_data(st.secrets["url_open_so"])
            
            if not df.empty:
                st.success(f"Data fetched successfully! Retrieved {len(df)} records.")
                st.dataframe(df)
            else:
                st.warning("No data retrieved from NetSuite.")
                logger.warning("DataFrame is empty after processing NetSuite data.")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.exception("Error in main function")

if __name__ == "__main__":
    main()