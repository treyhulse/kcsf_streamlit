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

def fetch_suiteql_data_with_date_pagination(query_template, start_date, end_date, step_days=30):
    """
    Fetch all data using date range pagination by batching queries by date ranges.
    Args:
        query_template (str): The SuiteQL query template without the date condition.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
        step_days (int): Number of days to fetch in each batch.

    Returns:
        pd.DataFrame: The combined DataFrame with all results.
    """
    import datetime
    all_data = pd.DataFrame()

    current_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    current_end = current_start + datetime.timedelta(days=step_days)

    final_end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    while current_start <= final_end:
        # Adjust date range if it exceeds the final end date
        if current_end > final_end:
            current_end = final_end

        # Format the date strings for the query
        current_start_str = current_start.strftime("%Y-%m-%d")
        current_end_str = current_end.strftime("%Y-%m-%d")

        # Create the paginated query
        paginated_query = query_template.format(start_date=current_start_str, end_date=current_end_str)

        # Fetch the data
        data_chunk = fetch_suiteql_data(paginated_query)

        # Break if no more data is returned
        if data_chunk.empty:
            break

        # Append the data chunk to the overall data
        all_data = pd.concat([all_data, data_chunk], ignore_index=True)

        # Update the start date for the next batch
        current_start = current_end + datetime.timedelta(days=1)
        current_end = current_start + datetime.timedelta(days=step_days)

    return all_data  # Return the combined DataFrame

# SuiteQL query to fetch inventory balance
suiteql_inventory_query = """
SELECT 
    item.id AS item_id,
    item.itemid AS item_name,
    balance.location AS location_name,
    balance.quantityonhand AS quantity_on_hand,
    balance.quantityavailable AS quantity_available
FROM 
    item
JOIN 
    inventorybalance AS balance ON item.id = balance.item
WHERE 
    item.isinactive = 'F'
ORDER BY 
    item_name ASC;
"""

@st.cache_data(ttl=900)
def fetch_netsuite_inventory():
    return fetch_suiteql_data(suiteql_inventory_query)
