import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
    return client

# Fetch all saved charts from the 'charts' collection
def get_all_charts(client):
    db = client['netsuite']
    charts_collection = db['charts']
    charts = list(charts_collection.find({}))
    return charts

# Fetch all dashboards from the 'dashboards' collection
def get_all_dashboards(client):
    db = client['netsuite']
    dashboards_collection = db['dashboards']
    dashboards = list(dashboards_collection.find({}))
    return dashboards

# Create or update a dashboard
def save_dashboard(client, dashboard_name, selected_chart_ids):
    db = client['netsuite']
    dashboards_collection = db['dashboards']
    
    dashboard_data = {
        "dashboard_name": dashboard_name,
        "selected_charts": selected_chart_ids,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Check if the dashboard already exists
    existing_dashboard = dashboards_collection.find_one({"dashboard_name": dashboard_name})
    if existing_dashboard:
        # Update the existing dashboard
        dashboards_collection.update_one({"dashboard_name": dashboard_name}, {"$set": dashboard_data})
        st.success(f"Dashboard '{dashboard_name}' updated successfully!")
    else:
        # Create a new dashboard
        dashboards_collection.insert_one(dashboard_data)
        st.success(f"Dashboard '{dashboard_name}' created successfully!")

# Delete a dashboard
def delete_dashboard(client, dashboard_name):
    db = client['netsuite']
    dashboards_collection = db['dashboards']
    dashboards_collection.delete_one({"dashboard_name": dashboard_name})
    st.success(f"Dashboard '{dashboard_name}' deleted successfully!")

# Main function to setup dashboard creation and chart assignment
def main():
    st.title("Dashboard Setup")
    
    client = get_mongo_client()
    
    # Step 1: Create or Update Dashboard
    st.subheader("Create or Update Dashboard")
    
    dashboard_name = st.text_input("Dashboard Name")
    
    # Step 2: Show all available charts to assign to the dashboard
    charts = get_all_charts(client)
    
    if charts:
        # Check if chart_config and chart_title exist
        chart_names = [f"{chart['chart_config'].get('chart_title', 'Untitled Chart')}" for chart in charts if 'chart_config' in chart]
        selected_charts = st.multiselect("Select Charts to Add to Dashboard", chart_names)
        
        # Get the selected chart IDs for saving
        selected_chart_ids = [chart['_id'] for chart in charts if chart['chart_config'].get('chart_title') in selected_charts]
        
        # Save or update the dashboard
        if st.button("Save Dashboard"):
            save_dashboard(client, dashboard_name, selected_chart_ids)
    
    # Step 3: Manage Dashboards (View existing dashboards, update, or delete them)
    st.subheader("Manage Dashboards")
    
    dashboards = get_all_dashboards(client)
    
    if dashboards:
        dashboard_names = [dashboard['dashboard_name'] for dashboard in dashboards]
        selected_dashboard = st.selectbox("Select Dashboard to Update/Delete", dashboard_names)
        
        if selected_dashboard:
            if st.button("Delete Dashboard"):
                delete_dashboard(client, selected_dashboard)

if __name__ == "__main__":
    main()
