# utils/apis.py
import requests
import pandas as pd
from io import StringIO
import logging
import streamlit as st
from utils.connections import get_authentication
import time

# Setup logging for error tracking
logging.basicConfig(level=logging.INFO)

# Fetch all data from NetSuite RESTlet that returns CSV
def fetch_all_data_csv(url, max_retries=3):
    """
    Fetch all paginated data from a NetSuite RESTlet that returns CSV.
    The data is combined into a single DataFrame.
    """
    all_data = []
    page = 1
    auth = get_authentication()

    if auth is None:
        return pd.DataFrame()  # Return empty DataFrame if authentication failed

    while True:
        for attempt in range(max_retries):
            try:
                logging.info(f"Fetching page {page} from {url}")
                response = requests.get(f"{url}&page={page}", auth=auth)
                response.raise_for_status()

                # Assume the response is CSV, parse the response text
                df = pd.read_csv(StringIO(response.text))

                if df.empty:
                    logging.info("Received empty dataframe. No more data.")
                    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

                all_data.append(df)
                logging.info(f"Fetched {len(df)} records from page {page}")

                # If we get less than 1000 records, assume it’s the last page
                if len(df) < 1000:
                    return pd.concat(all_data, ignore_index=True)

                page += 1
                break  # Success, go to the next page
            except Exception as e:
                logging.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    st.error(f"Failed to fetch data after {max_retries} attempts.")
                    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
                time.sleep(2 ** attempt)  # Exponential backoff
