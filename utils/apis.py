# utils/apis.py
import requests
import pandas as pd
from io import StringIO
import logging
import streamlit as st
import time
from utils.connections import get_authentication

# Setup logging
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

                # Assume the response is CSV
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

# Fetch all data from NetSuite RESTlet that returns JSON
def fetch_all_data_json(url, max_retries=3):
    """
    Fetch all paginated data from a NetSuite RESTlet that returns JSON.
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

                # Assuming the response is in JSON format
                data = response.json()

                if not data or len(data) == 0:
                    logging.info("Received empty data. No more data.")
                    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

                all_data.extend(data)
                logging.info(f"Fetched {len(data)} records from page {page}")

                # If we get less than 1000 records, assume it’s the last page
                if len(data) < 1000:
                    return pd.DataFrame(all_data)

                page += 1
                break  # Success, go to the next page
            except Exception as e:
                logging.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    st.error(f"Failed to fetch data after {max_retries} attempts.")
                    return pd.DataFrame(all_data) if all_data else pd.DataFrame()
                time.sleep(2 ** attempt)  # Exponential backoff

# Replace internal IDs with their corresponding display values
def replace_ids_with_display_values(df, mapping_dict):
    """
    Replace internal IDs (e.g., sales reps) with their display names.
    """
    if 'salesrep' in df.columns:
        df['salesrep'] = df['salesrep'].replace(mapping_dict)
    return df
