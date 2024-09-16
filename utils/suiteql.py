# utils.py
import requests
from requests_oauthlib import OAuth1
import streamlit as st
import pandas as pd
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication setup for all pages
def get_authentication():
    """
    This function returns an OAuth1 object for authenticating requests.
    It reads credentials from st.secrets.
    """
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

def fetch_suiteql_data(query, max_retries=3):
    """
    This function fetches data from NetSuite's SuiteQL API.
    
    Args:
        query (str): The SuiteQL query string.
        max_retries (int): Maximum retry attempts in case of failure.
    
    Returns:
        pd.DataFrame: DataFrame containing the results of the query.
    """
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


def fetch_suiteql_data_with_pagination(query, limit=1000):
    """
    Fetch all data using pagination by incrementing internalid.
    """
    all_data = pd.DataFrame()  # Initialize an empty DataFrame
    last_internal_id = 0  # Start with 0 or a minimum known internal ID
    
    while True:
        # Modify the query to fetch records greater than the last fetched internal ID
        paginated_query = f"""
        {query} AND transaction.internalid > {last_internal_id}
        ORDER BY transaction.internalid ASC
        LIMIT {limit}
        """
        
        # Fetch the data
        data_chunk = fetch_suiteql_data(paginated_query)
        
        # Break if no more data is returned
        if data_chunk.empty:
            logger.info("No more data to fetch.")
            break
        
        # Append the data chunk to the overall data
        all_data = pd.concat([all_data, data_chunk], ignore_index=True)
        
        # Update last_internal_id to the highest internal ID from the current chunk
        last_internal_id = data_chunk['internalid'].max()
        
        # Sleep to avoid overloading the server (optional)
        time.sleep(1)
    
    return all_data  # Return the combined DataFrame

