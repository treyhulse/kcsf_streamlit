from apscheduler.schedulers.background import BackgroundScheduler
from utils.netsuite_connection_manager import NetSuiteConnectionManager
import logging

logger = logging.getLogger(__name__)

def setup_sync_scheduler():
    scheduler = BackgroundScheduler()
    connection_manager = NetSuiteConnectionManager()

    def sync_all_connections():
        connections = connection_manager.get_connections()
        for conn in connections:
            success, message = connection_manager.incremental_update(conn['name'])
            if success:
                logger.info(f"Successfully updated connection {conn['name']}: {message}")
            else:
                logger.error(f"Failed to update connection {conn['name']}: {message}")

    # Schedule sync for all connections daily at 1 AM
    scheduler.add_job(sync_all_connections, 'cron', hour=1)

    scheduler.start()
    logger.info("Sync scheduler started")

    return scheduler