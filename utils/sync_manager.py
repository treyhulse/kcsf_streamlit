from utils.netsuite_client import NetSuiteClient
from utils.mongo_connection import get_mongo_client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SyncManager:
    def __init__(self):
        self.netsuite_client = NetSuiteClient()
        self.mongo_client = get_mongo_client()
        self.db = self.mongo_client['netsuite']

    def sync_inventory(self):
        inventory_data = self.netsuite_client.fetch_inventory_data()
        if inventory_data:
            collection = self.db['inventory']
            for item in inventory_data:
                collection.update_one(
                    {"Internal ID": item["Internal ID"]},
                    {"$set": item},
                    upsert=True
                )
            logger.info(f"Synced {len(inventory_data)} inventory items")
        else:
            logger.error("Failed to fetch inventory data from NetSuite")

    def sync_sales(self):
        sales_data = self.netsuite_client.fetch_sales_data()
        if sales_data:
            collection = self.db['sales']
            for sale in sales_data:
                collection.update_one(
                    {"Transaction ID": sale["Transaction ID"]},
                    {"$set": sale},
                    upsert=True
                )
            logger.info(f"Synced {len(sales_data)} sales records")
        else:
            logger.error("Failed to fetch sales data from NetSuite")

    def sync_items(self):
        items_data = self.netsuite_client.fetch_items_data()
        if items_data:
            collection = self.db['items']
            for item in items_data:
                collection.update_one(
                    {"Internal ID": item["Internal ID"]},
                    {"$set": item},
                    upsert=True
                )
            logger.info(f"Synced {len(items_data)} items")
        else:
            logger.error("Failed to fetch items data from NetSuite")

    def perform_full_sync(self):
        logger.info("Starting full sync")
        self.sync_inventory()
        self.sync_sales()
        self.sync_items()
        logger.info("Full sync completed")

    def log_sync_event(self, sync_type, status):
        collection = self.db['sync_logs']
        log_entry = {
            "sync_type": sync_type,
            "status": status,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(log_entry)

    def get_last_sync_time(self, sync_type):
        collection = self.db['sync_logs']
        last_sync = collection.find_one(
            {"sync_type": sync_type, "status": "success"},
            sort=[("timestamp", -1)]
        )
        return last_sync['timestamp'] if last_sync else None

    # Add more sync methods as needed