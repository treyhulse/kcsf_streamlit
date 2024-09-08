# utils/apis.py
import requests
import pandas as pd
import logging
import streamlit as st
from utils.connections import get_authentication

# Setup logging for error tracking
logging.basicConfig(level=logging.INFO)

# Fetch all data from NetSuite RESTlet that returns JSON
def fetch_all_data_json(url, max_retries=3):
    """
    Fetch all paginated data from a NetSuite RESTlet that returns JSON.
    The data is combined into a single DataFrame.
    """
    all_data = []
    auth = get_authentication()

    if auth is None:
        return pd.DataFrame()  # Return empty DataFrame if authentication failed

    # Retry mechanism in case of failed attempts
    for attempt in range(max_retries):
        try:
            logging.info(f"Fetching data from {url}")
            response = requests.get(url, auth=auth)
            response.raise_for_status()

            # Parse the response as JSON
            data = response.json()

            if not data or len(data) == 0:
                logging.info("Received empty data. No more records.")
                return pd.DataFrame(all_data) if all_data else pd.DataFrame()

            # Append the data
            all_data.extend(data)
            logging.info(f"Fetched {len(data)} records from the RESTlet.")
            return pd.DataFrame(all_data)
        except Exception as e:
            logging.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                st.error(f"Failed to fetch data after {max_retries} attempts.")
                return pd.DataFrame(all_data) if all_data else pd.DataFrame()
