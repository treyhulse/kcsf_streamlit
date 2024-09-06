import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.netsuite_connection_manager import NetSuiteConnectionManager
import pandas as pd

# Authentication check
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

page_name = 'NetSuite Connections'
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.title("NetSuite Connections Management")

connection_manager = NetSuiteConnectionManager()

# Add new connection
st.header("Add New Connection")
with st.form("new_connection"):
    name = st.text_input("Connection Name")
    saved_search_id = st.text_input("Saved Search ID")
    restlet_url = st.text_input("RESTlet URL")
    submitted = st.form_submit_button("Save Connection")
    if submitted:
        connection_manager.save_connection(name, saved_search_id, restlet_url)
        st.success("Connection saved successfully!")

# List existing connections
st.header("Existing Connections")
connections = connection_manager.get_connections()
for conn in connections:
    with st.expander(conn['name']):
        st.write(f"Saved Search ID: {conn['saved_search_id']}")
        st.write(f"RESTlet URL: {conn['restlet_url']}")
        if st.button(f"Delete {conn['name']}", key=f"delete_{conn['name']}"):
            connection_manager.delete_connection(conn['name'])
            st.experimental_rerun()

# Bulk upload
st.header("Bulk Upload")
selected_connection = st.selectbox("Select Connection for Bulk Upload", [conn['name'] for conn in connections])
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None and st.button("Upload CSV"):
    success, message = connection_manager.bulk_upload_csv(selected_connection, uploaded_file)
    if success:
        st.success(message)
    else:
        st.error(message)

# Incremental update
st.header("Incremental Update")
update_connection = st.selectbox("Select Connection for Update", [conn['name'] for conn in connections])
if st.button("Run Incremental Update"):
    success, message = connection_manager.incremental_update(update_connection)
    if success:
        st.success(message)
    else:
        st.error(message)