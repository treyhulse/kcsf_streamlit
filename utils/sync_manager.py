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

    def sync_data(self, data_type):
        try:
            fetch_method = getattr(self.netsuite_client, f"fetch_{data_type}_data")
            data = fetch_method()
            if data:
                collection = self.db[data_type]
                for item in data:
                    collection.update_one(
                        {"Internal ID": item["Internal ID"]},
                        {"$set": item},
                        upsert=True
                    )
                self.log_sync_event(data_type, "success", f"Synced {len(data)} {data_type} items")
                logger.info(f"Synced {len(data)} {data_type} items")
                return True
            else:
                self.log_sync_event(data_type, "failed", f"Failed to fetch {data_type} data from NetSuite")
                logger.error(f"Failed to fetch {data_type} data from NetSuite")
                return False
        except Exception as e:
            self.log_sync_event(data_type, "failed", f"Error during {data_type} sync: {str(e)}")
            logger.exception(f"Error during {data_type} sync")
            return False

    def perform_full_sync(self):
        try:
            sync_results = {}
            for data_type in ["inventory", "sales", "items"]:
                sync_results[data_type] = self.sync_data(data_type)
            
            if all(sync_results.values()):
                self.log_sync_event("full_sync", "success", "Full sync completed successfully")
                return True
            else:
                failed_syncs = [data_type for data_type, result in sync_results.items() if not result]
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