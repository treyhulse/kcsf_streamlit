import pandas as pd
import requests
from requests_oauthlib import OAuth1
import time
import logging
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from config import get_netsuite_config, API_URLS

# Rest of the code remains the same...

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_authentication():
    netsuite_config = get_netsuite_config()
    return OAuth1(
        netsuite_config["consumer_key"],
        netsuite_config["consumer_secret"],
        netsuite_config["token_key"],
        netsuite_config["token_secret"],
        realm=netsuite_config["realm"],
        signature_method='HMAC-SHA256'
    )

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_data(url: str, page: int = 1) -> Dict[str, Any]:
    """Fetch data from a NetSuite RESTlet endpoint."""
    auth = get_authentication()
    response = requests.get(f"{url}&page={page}", auth=auth)
    response.raise_for_status()
    return response.json()

def process_netsuite_data(url: str) -> pd.DataFrame:
    """Fetch and process NetSuite data."""
    all_data = []
    page = 1
    while True:
        data = fetch_data(url, page)
        all_data.extend(data['results'])
        if not data['hasMore']:
            break
        page += 1
    return pd.DataFrame(all_data)

def replace_ids_with_display_values(df: pd.DataFrame, mapping_dict: Dict[int, str], column_name: str) -> pd.DataFrame:
    """Replace internal IDs with their corresponding display values using a provided mapping."""
    df[column_name] = df[column_name].replace(mapping_dict)
    return df