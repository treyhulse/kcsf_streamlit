# utils.suiteql.py
import requests
from requests_oauthlib import OAuth1
import streamlit as st
import pandas as pd
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication setup for SuiteQL requests
def get_authentication():
    """
    Returns an OAuth1 object for authenticating SuiteQL requests.
    Credentials are stored in st.secrets.
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
    Fetches data from NetSuite's SuiteQL API.
    
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
            
            # Log the response status
            logger.info(f"Response status code: {response.status_code}")
            
            # Check if the request was successful
            response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
            
            # Assuming the response is in JSON format
            data = response.json().get('items', [])
            logger.info(f"Response JSON: {response.json()}")  # Log the full JSON response
            
            if not data:
                logger.info("No data returned.")
                return pd.DataFrame(all_data) if all_data else pd.DataFrame()

            all_data.extend(data)
            logger.info(f"Successfully fetched {len(data)} records.")
            return pd.DataFrame(all_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
            st.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")  # Display error in Streamlit
            if attempt == max_retries - 1:
                st.error(f"Failed to fetch data after {max_retries} attempts.")
                return pd.DataFrame(all_data) if all_data else pd.DataFrame()
            time.sleep(2 ** attempt)  # Exponential backoff



def fetch_paginated_suiteql_data(query, base_url):
    """
    Fetches paginated data from SuiteQL by following 'next' links.
    
    Args:
        query (str): SuiteQL query.
        base_url (str): Base URL for NetSuite's SuiteQL API.
    
    Returns:
        pd.DataFrame: A DataFrame containing all paginated results.
    """
    # Placeholder OAuth1 authentication or replace with your own method
    auth = OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )
    
    all_data = []
    next_url = base_url
    payload = {"q": query}

    while next_url:
        try:
            response = requests.post(next_url, auth=auth, json=payload, headers={"Content-Type": "application/json", "Prefer": "transient"})
            response.raise_for_status()  # Raise error for bad responses

            data = response.json()
            items = data.get("items", [])

            if not items:
                break

            all_data.extend(items)

            # Check if there's a next page
            links = data.get("links", [])
            next_link = next((link['href'] for link in links if link['rel'] == 'next'), None)
            next_url = next_link if next_link else None

        except Exception as e:
            print(f"Error fetching data: {e}")
            break

    return pd.DataFrame(all_data)

# Base URL for SuiteQL API
base_url = f"https://{st.secrets['realm']}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"


def fetch_paginated_inventory_data():
    """
    Fetches the entire inventory balance data from NetSuite using SuiteQL in paginated requests.
    
    Returns:
        pd.DataFrame: DataFrame containing all the inventory balance results.
    """
    all_data = []
    offset = 0
    page_size = 1000  # NetSuite's SuiteQL limit is typically 1,000 records per query

    while True:
        # Paginate through results using OFFSET
        suiteql_inventory_query = f"""
        SELECT
            invbal.item AS "Item ID",
            item.displayname AS "Item",
            invbal.binnumber AS "Bin Number",
            invbal.location AS "Warehouse",
            invbal.inventorynumber AS "Inventory Number",
            invbal.quantityonhand AS "Quantity On Hand",
            invbal.quantityavailable AS "Quantity Available"
        FROM
            inventorybalance invbal
        JOIN
            item ON invbal.item = item.id
        WHERE
            item.isinactive = 'F'
        ORDER BY
            item.displayname ASC
        OFFSET {offset}
        FETCH NEXT {page_size} ROWS ONLY;
        """
        
        # Fetch data for the current page
        df = fetch_suiteql_data(suiteql_inventory_query)
        
        # Break the loop if no more data is returned
        if df.empty:
            break
        
        # Append the current page data to the full dataset
        all_data.append(df)
        offset += page_size  # Move to the next page

    # Concatenate all the pages into a single DataFrame
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()



