import requests
from requests_oauthlib import OAuth1
import streamlit as st
import logging
import json

logger = logging.getLogger(__name__)

class NetSuiteClient:
    def __init__(self):
        self.auth = OAuth1(
            st.secrets["consumer_key"],
            st.secrets["consumer_secret"],
            st.secrets["token_key"],
            st.secrets["token_secret"],
            realm=st.secrets["realm"],
            signature_method='HMAC-SHA256'
        )
        self.base_url = st.secrets["netsuite_base_url"]

    def fetch_data(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"Fetching data from URL: {url}")
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from NetSuite: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None

    def fetch_inventory_data(self):
        logger.info("Fetching inventory data")
        return self.fetch_data("inventory")

    def fetch_sales_data(self):
        logger.info("Fetching sales data")
        return self.fetch_data("sales")

    def fetch_items_data(self):
        logger.info("Fetching items data")
        return self.fetch_data("items")

    # Test method to check API connection
    def test_connection(self):
        logger.info("Testing API connection")
        try:
            response = requests.get(f"{self.base_url}/test", auth=self.auth)
            response.raise_for_status()
            logger.info("API connection test successful")
            return True
        except requests.RequestException as e:
            logger.error(f"API connection test failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return False