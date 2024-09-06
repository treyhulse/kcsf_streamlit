import streamlit as st
from sync_manager import SyncManager
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Authentication check
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

if not validate_page_access(user_email, 'NetSuite_Sync.py'):
    show_permission_violation()

st.title("NetSuite Sync Management")

sync_manager = SyncManager()

st.header("Sync Options")

if st.button("Perform Full Sync"):
    with st.spinner("Performing full sync..."):
        sync_manager.perform_full_sync()
    st.success("Full sync completed!")

st.header("Individual Sync Options")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Sync Inventory"):
        with st.spinner("Syncing inventory..."):
            sync_manager.sync_inventory()
        st.success("Inventory sync completed!")

with col2:
    if st.button("Sync Sales"):
        with st.spinner("Syncing sales..."):
            sync_manager.sync_sales()
        st.success("Sales sync completed!")

with col3:
    if st.button("Sync Items"):
        with st.spinner("Syncing items..."):
            sync_manager.sync_items()
        st.success("Items sync completed!")

st.header("Sync Logs")

# Display recent sync logs
sync_logs = sync_manager.db['sync_logs'].find().sort("timestamp", -1).limit(10)
for log in sync_logs:
    st.write(f"{log['timestamp']}: {log['sync_type']} - {log['status']}")

# Add more UI elements for sync status, scheduling, etc.