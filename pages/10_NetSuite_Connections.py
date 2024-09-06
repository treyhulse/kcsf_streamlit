import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.netsuite_connection_manager import NetSuiteConnectionManager
import pandas as pd
from datetime import datetime
import plotly.express as px

# Authentication check
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

page_name = 'NetSuite Connections'
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.set_page_config(page_title="NetSuite Connections Management", layout="wide")

@st.cache_resource
def get_connection_manager():
    return NetSuiteConnectionManager()

connection_manager = get_connection_manager()

st.title("NetSuite Connections Management")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Manage Connections", "View Data", "Sync Status"])

if page == "Manage Connections":
    st.header("Manage NetSuite Connections")

    # Add new connection
    with st.expander("Add New Connection", expanded=False):
        with st.form("new_connection"):
            name = st.text_input("Connection Name")
            saved_search_id = st.text_input("Saved Search ID")
            restlet_url = st.text_input("RESTlet URL", value="/app/site/hosting/restlet.nl?script=customscript_general_purpose_restlet&deploy=1")
            sync_schedule = st.selectbox(
                "Sync Schedule",
                ["Manual", "Hourly", "Daily", "Weekly"]
            )
            submitted = st.form_submit_button("Save Connection")
            if submitted:
                try:
                    connection_manager.save_connection(name, saved_search_id, restlet_url, sync_schedule)
                    st.success("Connection saved successfully!")
                except Exception as e:
                    st.error(f"Error saving connection: {str(e)}")

    # List and manage existing connections
    st.subheader("Existing Connections")
    connections = connection_manager.get_connections()
    for conn in connections:
        with st.expander(conn['name']):
            st.write(f"Saved Search ID: {conn['saved_search_id']}")
            st.write(f"RESTlet URL: {conn['restlet_url']}")
            st.write(f"Last Sync: {conn.get('last_sync', 'Never')}")
            st.write(f"Sync Schedule: {conn['sync_schedule']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"Sync Now", key=f"sync_{conn['name']}"):
                    with st.spinner("Syncing data..."):
                        success, message = connection_manager.sync_connection_data(conn['name'])
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
            
            with col2:
                new_schedule = st.selectbox(
                    "Update Schedule",
                    ["Manual", "Hourly", "Daily", "Weekly"],
                    index=["Manual", "Hourly", "Daily", "Weekly"].index(conn['sync_schedule']),
                    key=f"schedule_{conn['name']}"
                )
                if st.button("Update Schedule", key=f"update_schedule_{conn['name']}"):
                    connection_manager.set_sync_schedule(conn['name'], new_schedule)
                    st.success(f"Schedule updated to {new_schedule}")
            
            with col3:
                if st.button(f"Delete Connection", key=f"delete_{conn['name']}"):
                    if st.checkbox(f"Confirm deletion of {conn['name']}"):
                        connection_manager.delete_connection(conn['name'])
                        st.success(f"Connection {conn['name']} deleted")
                        st.experimental_rerun()

elif page == "View Data":
    st.header("View Connection Data")

    # Select connection
    connections = connection_manager.get_connections()
    connection_names = [conn['name'] for conn in connections]
    selected_connection = st.selectbox("Select Connection", connection_names)

    if selected_connection:
        # Get data for selected connection
        df = connection_manager.get_connection_data(selected_connection)
        
        # Display basic info
        st.write(f"Total records: {len(df)}")
        st.write(f"Columns: {', '.join(df.columns)}")

        # Data preview
        st.subheader("Data Preview")
        st.dataframe(df.head())

        # Column selection for detailed view
        selected_columns = st.multiselect("Select columns to view", df.columns)
        if selected_columns:
            st.dataframe(df[selected_columns])

        # Basic data visualization
        st.subheader("Data Visualization")
        if len(df) > 0:
            numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_columns) > 0:
                x_axis = st.selectbox("Select X-axis", numeric_columns)
                y_axis = st.selectbox("Select Y-axis", numeric_columns)
                chart_type = st.radio("Select chart type", ["Scatter", "Line", "Bar"])
                
                if chart_type == "Scatter":
                    fig = px.scatter(df, x=x_axis, y=y_axis)
                elif chart_type == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis)
                else:
                    fig = px.bar(df, x=x_axis, y=y_axis)
                
                st.plotly_chart(fig)
        else:
            st.write("No data available for visualization.")

        # Download option
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f"{selected_connection}_data.csv",
                mime="text/csv",
            )

elif page == "Sync Status":
    st.header("Sync Status Overview")

    # Display last sync time for each connection
    st.subheader("Last Sync Times")
    connections = connection_manager.get_connections()
    for conn in connections:
        last_sync = conn.get('last_sync', "Never")
        st.write(f"{conn['name']}: {last_sync}")

    # Option to sync all connections
    if st.button("Sync All Connections"):
        with st.spinner("Syncing all connections..."):
            results = []
            for conn in connections:
                success, message = connection_manager.sync_connection_data(conn['name'])
                results.append({"name": conn['name'], "success": success, "message": message})
            
            # Display results
            for result in results:
                if result['success']:
                    st.success(f"{result['name']}: {result['message']}")
                else:
                    st.error(f"{result['name']}: {result['message']}")

    # Sync history
    st.subheader("Sync History")
    history = connection_manager.get_sync_history()
    if history:
        history_df = pd.DataFrame(history)
        st.dataframe(history_df)
    else:
        st.write("No sync history available.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("NetSuite Connections Manager v1.0")
st.sidebar.text("© 2023 Your Company Name")