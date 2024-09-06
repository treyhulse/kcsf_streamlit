from apscheduler.schedulers.background import BackgroundScheduler
from sync_manager import SyncManager
import logging

logger = logging.getLogger(__name__)

def setup_sync_scheduler():
    scheduler = BackgroundScheduler()
    sync_manager = SyncManager()

    # Schedule full sync daily at 1 AM
    scheduler.add_job(sync_manager.perform_full_sync, 'cron', hour=1)

    # Schedule inventory sync every 4 hours
    scheduler.add_job(sync_manager.sync_inventory, 'interval', hours=4)

    # Schedule sales sync every 2 hours
    scheduler.add_job(sync_manager.sync_sales, 'interval', hours=2)

    # Schedule items sync every 6 hours
    scheduler.add_job(sync_manager.sync_items, 'interval', hours=6)

    scheduler.start()
    logger.info("Sync scheduler started")

    return scheduler