import streamlit as st
import pandas as pd
from pymongo import MongoClient
from utils.mongo_connection import get_mongo_client
import requests
from requests_oauthlib import OAuth1
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NetSuiteConnectionManager:
    def __init__(self):
        self.mongo_client = get_mongo_client()
        self.db = self.mongo_client['netsuite']
        self.connections_collection = self.db['netsuite_connections']
        self.auth = OAuth1(
            st.secrets["consumer_key"],
            st.secrets["consumer_secret"],
            st.secrets["token_key"],
            st.secrets["token_secret"],
            realm=st.secrets["realm"],
            signature_method='HMAC-SHA256'
        )
        self.base_url = st.secrets["netsuite_base_url"]

    def save_connection(self, name, saved_search_id, restlet_url):
        connection = {
            "name": name,
            "saved_search_id": saved_search_id,
            "restlet_url": restlet_url,
            "last_sync": None
        }
        self.connections_collection.update_one(
            {"name": name},
            {"$set": connection},
            upsert=True
        )

    def get_connections(self):
        return list(self.connections_collection.find())

    def delete_connection(self, name):
        self.connections_collection.delete_one({"name": name})
        # Also delete the corresponding data collection
        self.db[name].drop()

    def fetch_data_from_restlet(self, restlet_url, params=None):
        try:
            response = requests.get(f"{self.base_url}/{restlet_url}", auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from RESTlet: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None

    def sync_connection_data(self, connection_name):
        connection = self.connections_collection.find_one({"name": connection_name})
        if not connection:
            return False, "Connection not found"

        try:
            # Fetch data from RESTlet
            data = self.fetch_data_from_restlet(connection['restlet_url'])

            if data:
                # Update MongoDB
                collection = self.db[connection_name]
                collection.delete_many({})  # Clear existing data
                collection.insert_many(data)

                # Update last sync timestamp
                self.connections_collection.update_one(
                    {"name": connection_name},
                    {"$set": {"last_sync": datetime.utcnow()}}
                )

                return True, f"Successfully synced {len(data)} records"
            else:
                return False, "No data received from RESTlet"

        except Exception as e:
            logger.error(f"Error during data sync: {str(e)}")
            return False, str(e)

    def get_connection_data(self, connection_name):
        collection = self.db[connection_name]
        data = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB _id field
        return pd.DataFrame(data)

    def set_sync_schedule(self, connection_name, schedule):
        self.connections_collection.update_one(
            {"name": connection_name},
            {"$set": {"sync_schedule": schedule}}
        )