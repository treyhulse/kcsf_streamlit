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
            "restlet_url": restlet_url
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

    def bulk_upload_csv(self, connection_name, csv_file):
        connection = self.connections_collection.find_one({"name": connection_name})
        if not connection:
            return False, "Connection not found"

        try:
            df = pd.read_csv(csv_file)
            data = df.to_dict('records')
            collection = self.db[connection_name]
            collection.insert_many(data)
            return True, f"Successfully uploaded {len(data)} records"
        except Exception as e:
            logger.error(f"Error during bulk upload: {str(e)}")
            return False, str(e)

    def incremental_update(self, connection_name):
        connection = self.connections_collection.find_one({"name": connection_name})
        if not connection:
            return False, "Connection not found"

        try:
            # Fetch last update timestamp
            last_update = self.db[f"{connection_name}_metadata"].find_one({"_id": "last_update"})
            last_update_time = last_update['timestamp'] if last_update else None

            # Fetch updated data from RESTlet
            params = {"last_update": last_update_time} if last_update_time else None
            updated_data = self.fetch_data_from_restlet(connection['restlet_url'], params)

            if updated_data:
                # Update MongoDB
                collection = self.db[connection_name]
                for item in updated_data:
                    collection.update_one(
                        {"id": item['id']},  # Assuming each item has a unique 'id' field
                        {"$set": item},
                        upsert=True
                    )

                # Update last update timestamp
                self.db[f"{connection_name}_metadata"].update_one(
                    {"_id": "last_update"},
                    {"$set": {"timestamp": datetime.utcnow()}},
                    upsert=True
                )

                return True, f"Successfully updated {len(updated_data)} records"
            else:
                return False, "No data received from RESTlet"

        except Exception as e:
            logger.error(f"Error during incremental update: {str(e)}")
            return False, str(e)