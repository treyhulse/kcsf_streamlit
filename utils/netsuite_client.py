import requests
from requests_oauthlib import OAuth1
import streamlit as st
import logging

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
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from NetSuite: {str(e)}")
            return None

    def fetch_inventory_data(self):
        return self.fetch_data("inventory")

    def fetch_sales_data(self):
        return self.fetch_data("sales")

    def fetch_items_data(self):
        return self.fetch_data("items")

    # Add more methods for other data types as needed