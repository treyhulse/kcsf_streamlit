import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
from typing import Dict, Any

from utils.config import get_netsuite_config, API_URLS

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
        try:
            data = fetch_data(url, page)
            if 'results' not in data or not data['results']:
                logger.warning(f"No results found on page {page}")
                break
            all_data.extend(data['results'])
            if not data.get('hasMore', False):
                break
            page += 1
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data on page {page}: {str(e)}")
            break
    
    if not all_data:
        logger.error("No data retrieved from NetSuite")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    logger.info(f"Retrieved {len(df)} records from NetSuite")
    return df

def replace_ids_with_display_values(df: pd.DataFrame, mapping_dict: Dict[int, str], column_name: str) -> pd.DataFrame:
    """Replace internal IDs with their corresponding display values using a provided mapping."""
    if column_name in df.columns:
        df[column_name] = df[column_name].replace(mapping_dict)
    else:
        logger.warning(f"Column '{column_name}' not found in DataFrame")
    return df