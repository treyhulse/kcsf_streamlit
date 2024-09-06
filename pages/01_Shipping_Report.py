import streamlit as st
import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_netsuite_auth():
    return OAuth1(
        st.secrets["netsuite"]["consumer_key"],
        st.secrets["netsuite"]["consumer_secret"],
        st.secrets["netsuite"]["token_key"],
        st.secrets["netsuite"]["token_secret"],
        realm=st.secrets["netsuite"]["realm"],
        signature_method='HMAC-SHA256'
    )

def fetch_data(url: str, page: int = 1) -> Dict[str, Any]:
    """Fetch data from a NetSuite RESTlet endpoint."""
    auth = get_netsuite_auth()
    response = requests.get(f"{url}&page={page}", auth=auth)
    response.raise_for_status()
    return response.json()

def process_netsuite_data(url: str) -> pd.DataFrame:
    """Fetch and process NetSuite data."""
    all_data = []
    page = 1
    while True:
        try:
            data = fetch_data(url, page)
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

def main():
    st.title("NetSuite Data Display")

    try:
        with st.spinner("Fetching data from NetSuite..."):
            df = process_netsuite_data(st.secrets["url_open_so"])
        
        if not df.empty:
            st.success(f"Data fetched successfully! Retrieved {len(df)} records.")
            st.dataframe(df)
        else:
            st.warning("No data retrieved from NetSuite.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.exception("Error in main function")

if __name__ == "__main__":
    main()