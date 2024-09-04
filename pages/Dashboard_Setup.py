import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import json

# MongoDB connection
def get_mongo_client():
    try:
        connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
        client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
        return client
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {str(e)}")
        return None

# Fetch all saved charts from the 'charts' collection
def get_all_charts(client):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        charts = list(charts_collection.find({}))
        return charts
    except Exception as e:
        st.error(f"Error fetching charts: {str(e)}")
        return []

# Fetch all dashboards from the 'dashboards' collection
def get_all_dashboards(client):
    try:
        db = client['netsuite']
        dashboards_collection = db['dashboards']
        dashboards = list(dashboards_collection.find({}))
        return dashboards
    except Exception as e:
        st.error(f"Error fetching dashboards: {str(e)}")
        return []

# Create or update a dashboard
def save_dashboard(client, dashboard_name, selected_chart_ids):
    try:
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
    except Exception as e:
        st.error(f"Error saving dashboard: {str(e)}")

# Delete a dashboard
def delete_dashboard(client, dashboard_name):
    try:
        db = client['netsuite']
        dashboards_collection = db['dashboards']
        dashboards_collection.delete_one({"dashboard_name": dashboard_name})
        st.success(f"Dashboard '{dashboard_name}' deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting dashboard: {str(e)}")

# Create a new chart
def save_chart(client, chart_title, chart_data):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        
        chart_data = {
            "chart_title": chart_title,
            "chart_config": chart_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create a new chart
        charts_collection.insert_one(chart_data)
        st.success(f"Chart '{chart_title}' created successfully!")
    except Exception as e:
        st.error(f"Error saving chart: {str(e)}")

# Update an existing chart
def update_chart(client, chart_id, chart_title, chart_data):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        
        # Update the existing chart
        charts_collection.update_one({"_id": chart_id}, {"$set": {
            "chart_title": chart_title,
            "chart_config": chart_data,
            "updated_at": datetime.utcnow()
        }})
        st.success(f"Chart '{chart_title}' updated successfully!")
    except Exception as e:
        st.error(f"Error updating chart: {str(e)}")

# Delete a chart
def delete_chart(client, chart_id):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        charts_collection.delete_one({"_id": chart_id})
        st.success("Chart deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting chart: {str(e)}")

# Main function to setup dashboard and chart management
def main():
    st.title("Dashboard and Chart Management")
    
    client = get_mongo_client()

    # Check MongoDB connection
    if client:
        # Dashboards section
        st.header("Dashboards")
        
        # Expandable section for creating a dashboard
        with st.expander("Create New Dashboard"):
            st.subheader("Create Dashboard")
            
            dashboard_name = st.text_input("New Dashboard Name")
            
            # Show available charts to assign to the dashboard
            charts = get_all_charts(client)
            
            if charts:
                chart_names = [f"{chart['chart_config'].get('chart_title', 'Untitled Chart')}" for chart in charts if 'chart_config' in chart]
                selected_charts = st.multiselect("Select Charts to Add to Dashboard", chart_names)
                
                # Get the selected chart IDs for saving
                selected_chart_ids = [chart['_id'] for chart in charts if chart['chart_config'].get('chart_title') in selected_charts]
                
                if st.button("Create Dashboard"):
                    save_dashboard(client, dashboard_name, selected_chart_ids)

        # Expandable section for updating an existing dashboard
        with st.expander("Update Existing Dashboard"):
            st.subheader("Update Dashboard")
            
            dashboards = get_all_dashboards(client)
            
            if dashboards:
                dashboard_names = [dashboard['dashboard_name'] for dashboard in dashboards]
                selected_dashboard = st.selectbox("Select Dashboard to Update", dashboard_names)
                
                if selected_dashboard:
                    # Show available charts to update the dashboard
                    charts = get_all_charts(client)
                    if charts:
                        chart_names = [f"{chart['chart_config'].get('chart_title', 'Untitled Chart')}" for chart in charts if 'chart_config' in chart]
                        selected_charts = st.multiselect("Select Charts to Update Dashboard", chart_names)
                        
                        selected_chart_ids = [chart['_id'] for chart in charts if chart['chart_config'].get('chart_title') in selected_charts]
                        
                        if st.button("Update Dashboard"):
                            save_dashboard(client, selected_dashboard, selected_chart_ids)

        # Expandable section for deleting a dashboard
        with st.expander("Delete Dashboard"):
            st.subheader("Delete Dashboard")
            
            dashboards = get_all_dashboards(client)
            
            if dashboards:
                dashboard_names = [dashboard['dashboard_name'] for dashboard in dashboards]
                selected_dashboard = st.selectbox("Select Dashboard to Delete", dashboard_names)
                
                if selected_dashboard:
                    if st.button("Delete Dashboard"):
                        delete_dashboard(client, selected_dashboard)

        # Charts section
        st.header("Charts")
        
        # Example chart config JSON structure
        example_chart_config = '''{
  "collection_name": "sales",
  "x_column": "Date",
  "y_column": "Amount",
  "color_column": "Sales Rep",
  "chart_type": "Bar",
  "selected_types": ["All"],
  "selected_statuses": ["Billed"],
  "chart_title": "Bar Chart of Amount vs Date"
}'''

        # Expandable section for creating a new chart
        with st.expander("Create New Chart"):
            st.subheader("Create Chart")
            
            chart_title = st.text_input("Chart Title")
            chart_config = st.text_area("Enter Chart Configuration (JSON format)", example_chart_config)
            
            if st.button("Create Chart"):
                try:
                    chart_data = json.loads(chart_config)  # Parse the JSON input
                    save_chart(client, chart_title, chart_data)
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON format: {str(e)}")
    
        # Expandable section for updating an existing chart
        with st.expander("Update Existing Chart"):
            st.subheader("Update Chart")
            
            charts = get_all_charts(client)
            
            if charts:
                chart_titles = [f"{chart['chart_config'].get('chart_title', 'Untitled Chart')}" for chart in charts]
                selected_chart = st.selectbox("Select Chart to Update", chart_titles)
                
                if selected_chart:
                    chart_id = next(chart['_id'] for chart in charts if chart['chart_config'].get('chart_title') == selected_chart)
                    new_chart_title = st.text_input("New Chart Title", value=selected_chart)
                    new_chart_config = st.text_area("Enter New Chart Configuration (JSON format)", example_chart_config)
                    
                    if st.button("Update Chart"):
                        try:
                            chart_data = json.loads(new_chart_config)  # Parse the updated JSON input
                            update_chart(client, chart_id, new_chart_title, chart_data)
                        except json.JSONDecodeError as e:
                            st.error(f"Invalid JSON format: {str(e)}")

        # Expandable section for deleting a chart
        with st.expander("Delete Chart"):
            st.subheader("Delete Chart")
            
            charts = get_all_charts(client)
            
            if charts:
                chart_titles = [f"{chart['chart_config'].get('chart_title', 'Untitled Chart')}" for chart in charts]
                selected_chart = st.selectbox("Select Chart to Delete", chart_titles)
                
                if selected_chart:
                    chart_id = next(chart['_id'] for chart in charts if chart['chart_config'].get('chart_title') == selected_chart)
                    
                    if st.button("Delete Chart"):
                        delete_chart(client, chart_id)
    else:
        st.error("Unable to connect to MongoDB. Please check your connection settings.")

if __name__ == "__main__":
    main()
