# utils.py
import requests
from requests_oauthlib import OAuth1
import streamlit as st

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
    import pandas as pd
    import time
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

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

import pandas as pd
import time

def fetch_suiteql_data_with_pagination(query, limit=1000):
    # Function to fetch all records by paginating
    offset = 0
    all_data = []
    
    while True:
        # Add pagination to the query
        paginated_query = f"{query} LIMIT {limit} OFFSET {offset}"
        
        # Fetch the data using your existing fetch_suiteql_data function
        data_chunk = fetch_suiteql_data(paginated_query)
        
        # Break if no more data is returned
        if data_chunk.empty:
            break
        
        # Append the data chunk to the overall data
        all_data.append(data_chunk)
        
        # Increment offset to fetch the next batch
        offset += limit
        
        # Sleep to avoid overloading the server (optional)
        time.sleep(1)
    
    # Combine all chunks into a single DataFrame
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data is fetched
