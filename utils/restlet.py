"""
NetSuite RESTlet Data Fetcher

This module handles authentication and data fetching from NetSuite RESTlets.
It provides OAuth1 authentication and converts JSON responses to pandas DataFrames.

Dependencies:
- requests: HTTP requests
- pandas: Data manipulation
- requests_oauthlib: OAuth1 authentication
- streamlit: Secrets management

Author: KCSF Development Team
"""

import requests
import pandas as pd
from requests_oauthlib import OAuth1
import logging
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_authentication():
    """
    Create OAuth1 authentication object for NetSuite API.
    
    Uses Streamlit secrets for secure credential management.
    
    Returns:
        OAuth1: Configured OAuth1 authentication object
        
    Required Secrets:
        - consumer_key: NetSuite consumer key
        - consumer_secret: NetSuite consumer secret
        - token_key: NetSuite token key
        - token_secret: NetSuite token secret
        - realm: NetSuite account realm
    """
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

def fetch_restlet_data(saved_search_id):
    """
    Fetch data from NetSuite RESTlet and convert to pandas DataFrame.
    
    This function authenticates with NetSuite, makes a RESTlet call,
    and returns the data as a pandas DataFrame for easy manipulation.
    
    Args:
        saved_search_id (str): NetSuite saved search ID to execute
        
    Returns:
        pd.DataFrame: Data from the RESTlet as a pandas DataFrame.
                     Returns empty DataFrame if no data or error occurs.
                     
    Raises:
        requests.exceptions.RequestException: If HTTP request fails
        
    Example:
        >>> df = fetch_restlet_data("customsearch5190")
        >>> print(f"Fetched {len(df)} records")
    """
    # Construct URL with saved search ID
    url = f"{st.secrets['url_restlet']}&savedSearchId={saved_search_id}"
    auth = get_authentication()
    
    try:
        logger.info(f"Fetching data from RESTlet with search ID: {saved_search_id}")
        
        # Make authenticated request to NetSuite RESTlet
        response = requests.get(
            url, 
            auth=auth, 
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse JSON response
        data = response.json()

        # Handle empty response
        if not data or len(data) == 0:
            logger.info(f"No data returned for search ID: {saved_search_id}")
            return pd.DataFrame()

        # Convert to pandas DataFrame
        df = pd.DataFrame(data)
        logger.info(f"Successfully fetched {len(df)} records from search ID: {saved_search_id}")
        return df

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from RESTlet: {e}")
        st.error(f"Failed to fetch data from NetSuite: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error while fetching data: {e}")
        st.error(f"Unexpected error: {e}")
        return pd.DataFrame()
