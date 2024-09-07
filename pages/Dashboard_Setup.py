import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Dashboard Setup'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################


from pymongo import MongoClient
from datetime import datetime


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

# Update the chart title within the chart_config
def update_chart_title_in_config(client, chart_id, chart_title):
    try:
        db = client['netsuite']
        charts_collection = db['charts']
        
        # Update the chart title inside chart_config
        charts_collection.update_one(
            {"_id": chart_id}, 
            {"$set": {
                "chart_config.chart_title": chart_title,
                "updated_at": datetime.utcnow()
            }}
        )
        st.success(f"Chart title within chart_config updated successfully!")
    except Exception as e:
        st.error(f"Error updating chart title within chart_config: {str(e)}")

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
        
        # Expandable section for updating an existing chart title within chart_config
        with st.expander("Update Existing Chart Title in Chart Config"):
            st.subheader("Update Chart Title")
            
            charts = get_all_charts(client)
            
            if charts:
                chart_titles = [f"{chart['chart_config'].get('chart_title', 'Untitled Chart')}" for chart in charts]
                selected_chart = st.selectbox("Select Chart to Update Title", chart_titles)
                
                if selected_chart:
                    chart_id = next(chart['_id'] for chart in charts if chart['chart_config'].get('chart_title') == selected_chart)
                    new_chart_title = st.text_input("New Chart Title", value=selected_chart)
                    
                    if st.button("Update Chart Title"):
                        update_chart_title_in_config(client, chart_id, new_chart_title)

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
