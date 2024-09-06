import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.sync_manager import SyncManager
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Authentication check
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

page_name = 'API Portal'
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.title("NetSuite Sync Management")

sync_manager = SyncManager()

st.header("Sync Options")

if st.button("Perform Full Sync"):
    with st.spinner("Performing full sync..."):
        result = sync_manager.perform_full_sync()
    if result:
        st.success("Full sync completed successfully!")
    else:
        st.error("Full sync encountered some issues. Check the logs for details.")

st.header("Individual Sync Options")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Sync Inventory"):
        with st.spinner("Syncing inventory..."):
            result = sync_manager.sync_data("inventory")
        if result:
            st.success("Inventory sync completed successfully!")
        else:
            st.error("Inventory sync encountered some issues. Check the logs for details.")

with col2:
    if st.button("Sync Sales"):
        with st.spinner("Syncing sales..."):
            result = sync_manager.sync_data("sales")
        if result:
            st.success("Sales sync completed successfully!")
        else:
            st.error("Sales sync encountered some issues. Check the logs for details.")

with col3:
    if st.button("Sync Items"):
        with st.spinner("Syncing items..."):
            result = sync_manager.sync_data("items")
        if result:
            st.success("Items sync completed successfully!")
        else:
            st.error("Items sync encountered some issues. Check the logs for details.")

st.header("Sync Logs")

# Display recent sync logs with more details
st.subheader("Recent Sync Logs")
sync_logs = sync_manager.get_recent_sync_logs(10)  # Get last 10 logs
if sync_logs:
    for log in sync_logs:
        status_color = "green" if log['status'] == "success" else "red"
        st.markdown(f"**{log['timestamp']}**: {log['sync_type']} - "
                    f"<span style='color:{status_color}'>{log['status']}</span>", unsafe_allow_html=True)
        if 'details' in log:
            st.text(f"Details: {log['details']}")
else:
    st.info("No sync logs found.")

# Display sync statistics
st.subheader("Sync Statistics")
stats = sync_manager.get_sync_statistics()
if stats:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Syncs", stats['total_syncs'])
    col2.metric("Successful Syncs", stats['successful_syncs'])
    col3.metric("Failed Syncs", stats['failed_syncs'])
    
    st.markdown(f"**Last Successful Sync:** {stats['last_successful_sync']}")
    st.markdown(f"**Last Failed Sync:** {stats['last_failed_sync']}")
else:
    st.info("No sync statistics available yet.")

# Add a section to view sync details for a specific date range
st.header("View Sync Details")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
with col2:
    end_date = st.date_input("End Date", datetime.now())

if st.button("View Sync Details"):
    details = sync_manager.get_sync_details(start_date, end_date)
    if details:
        st.dataframe(details)
    else:
        st.info("No sync details found for the selected date range.")