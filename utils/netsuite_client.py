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

    def make_request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, auth=self.auth, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error making request to NetSuite: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None

    def test_connection(self):
        return self.make_request('GET', 'test')