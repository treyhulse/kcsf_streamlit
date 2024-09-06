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
        try:
            inventory_data = self.netsuite_client.fetch_inventory_data()
            if inventory_data:
                collection = self.db['inventory']
                for item in inventory_data:
                    collection.update_one(
                        {"Internal ID": item["Internal ID"]},
                        {"$set": item},
                        upsert=True
                    )
                self.log_sync_event("inventory", "success", f"Synced {len(inventory_data)} inventory items")
                logger.info(f"Synced {len(inventory_data)} inventory items")
                return True
            else:
                self.log_sync_event("inventory", "failed", "Failed to fetch inventory data from NetSuite")
                logger.error("Failed to fetch inventory data from NetSuite")
                return False
        except Exception as e:
            self.log_sync_event("inventory", "failed", f"Error during inventory sync: {str(e)}")
            logger.exception("Error during inventory sync")
            return False

    def sync_sales(self):
        # Similar implementation to sync_inventory
        pass

    def sync_items(self):
        # Similar implementation to sync_inventory
        pass

    def perform_full_sync(self):
        try:
            inventory_success = self.sync_inventory()
            sales_success = self.sync_sales()
            items_success = self.sync_items()
            
            if inventory_success and sales_success and items_success:
                self.log_sync_event("full_sync", "success", "Full sync completed successfully")
                return True
            else:
                failed_syncs = []
                if not inventory_success: failed_syncs.append("inventory")
                if not sales_success: failed_syncs.append("sales")
                if not items_success: failed_syncs.append("items")
                self.log_sync_event("full_sync", "partial_success", f"Full sync completed with issues in: {', '.join(failed_syncs)}")
                return False
        except Exception as e:
            self.log_sync_event("full_sync", "failed", f"Error during full sync: {str(e)}")
            logger.exception("Error during full sync")
            return False

    def log_sync_event(self, sync_type, status, details):
        collection = self.db['sync_logs']
        log_entry = {
            "sync_type": sync_type,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(log_entry)

    def get_recent_sync_logs(self, limit=10):
        collection = self.db['sync_logs']
        return list(collection.find().sort("timestamp", -1).limit(limit))

    def get_sync_statistics(self):
        collection = self.db['sync_logs']
        total_syncs = collection.count_documents({})
        successful_syncs = collection.count_documents({"status": "success"})
        failed_syncs = collection.count_documents({"status": "failed"})
        
        last_successful = collection.find_one({"status": "success"}, sort=[("timestamp", -1)])
        last_failed = collection.find_one({"status": "failed"}, sort=[("timestamp", -1)])

        return {
            "total_syncs": total_syncs,
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "last_successful_sync": last_successful['timestamp'] if last_successful else "N/A",
            "last_failed_sync": last_failed['timestamp'] if last_failed else "N/A"
        }

    def get_sync_details(self, start_date, end_date):
        collection = self.db['sync_logs']
        return list(collection.find({
            "timestamp": {
                "$gte": datetime.combine(start_date, datetime.min.time()),
                "$lte": datetime.combine(end_date, datetime.max.time())
            }
        }).sort("timestamp", -1))

    def get_last_sync_time(self, sync_type):
        collection = self.db['sync_logs']
        last_sync = collection.find_one(
            {"sync_type": sync_type, "status": "success"},
            sort=[("timestamp", -1)]
        )
        return last_sync['timestamp'] if last_sync else None