import pandas as pd
import requests
from requests_oauthlib import OAuth1
from io import StringIO
import time
import logging
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication setup for both pages
def get_authentication():
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

# For Shipping Report: CSV Data Handling
def fetch_all_data_csv(url, max_retries=3):
    all_data = []
    page = 1
    auth = get_authentication()

    while True:
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{url}&page={page}", auth=auth)
                response.raise_for_status()

                # Print the raw response data
                st.write(response.text)  # Print raw CSV response

                # Convert the CSV response to a DataFrame
                df = pd.read_csv(StringIO(response.text))

                if df.empty:
                    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

                all_data.append(df)

                if len(df) < 1000:
                    return pd.concat(all_data, ignore_index=True)

                page += 1
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    st.error(f"Failed to fetch data after {max_retries} attempts.")
                    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()


# For Sales Dashboard: JSON Data Handling
def fetch_all_data_json(url, max_retries=3):
    """Fetch all data from a NetSuite RESTlet endpoint that returns JSON data."""
    all_data = []
    page = 1
    auth = get_authentication()

    while True:
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching page {page} from {url}")
                response = requests.get(f"{url}&page={page}", auth=auth)
                response.raise_for_status()

                # Assuming the response is in JSON format
                data = response.json()

                if not data or len(data) == 0:
                    logger.info("Received empty data. Assuming end of data.")
                    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

                all_data.extend(data)
                logger.info(f"Successfully fetched {len(data)} records from page {page}")

                if len(data) < 1000:  # Assuming 1000 is the max page size
                    logger.info("Received less than 1000 records. Assuming last page.")
                    return pd.DataFrame(all_data)

                page += 1
                break  # Success, move to next page
            except Exception as e:
                logger.error(f"Error fetching data on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    st.error(f"Failed to fetch data after {max_retries} attempts.")
                    return pd.DataFrame(all_data) if all_data else pd.DataFrame()
                time.sleep(2 ** attempt)  # Exponential backoff

def replace_ids_with_display_values(df, mapping_dict):
    """Replace internal IDs with their corresponding display values using a provided mapping."""
    if 'salesrep' in df.columns:
        df['salesrep'] = df['salesrep'].replace(mapping_dict)
    return df

def process_netsuite_data_csv(url):
    """Fetch and process NetSuite CSV data."""
    df = fetch_all_data_csv(url)
    return df

def process_netsuite_data_json(url, sales_rep_mapping):
    """Fetch and process NetSuite JSON data, replacing IDs with display values."""
    df = fetch_all_data_json(url)

    if not df.empty:
        df = replace_ids_with_display_values(df, sales_rep_mapping)
    
    return df
