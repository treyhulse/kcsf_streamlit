import streamlit as st
import plotly.express as px
from pymongo import MongoClient

# MongoDB connection
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
    return client

# Fetch all dashboards from the 'dashboards' collection
def get_all_dashboards(client):
    db = client['netsuite']
    dashboards_collection = db['dashboards']
    dashboards = list(dashboards_collection.find({}))
    return dashboards

# Fetch the selected dashboard
def get_dashboard(client, dashboard_name):
    db = client['netsuite']
    dashboards_collection = db['dashboards']
    dashboard = dashboards_collection.find_one({"dashboard_name": dashboard_name})
    return dashboard

# Fetch a chart by its ID
def get_chart_by_id(client, chart_id):
    db = client['netsuite']
    charts_collection = db['charts']
    chart = charts_collection.find_one({"_id": chart_id})
    return chart

# Render the selected charts for the given dashboard
def render_dashboard(client, dashboard_name):
    dashboard = get_dashboard(client, dashboard_name)
    
    if dashboard and 'selected_charts' in dashboard:
        chart_ids = dashboard['selected_charts']
        
        st.title(f"Dashboard: {dashboard_name}")
        
        # Display up to 4 charts, 3 per row
        cols = st.columns(3)
        chart_count = 0
        
        for chart_id in chart_ids[:4]:  # Limit to 4 charts
            chart = get_chart_by_id(client, chart_id)
            if chart:
                with cols[chart_count % 3]:  # Cycle through the 3 columns
                    chart_config = chart['chart_config']
                    st.subheader(chart_config['chart_title'])
                    
                    # Check if 'data' exists in chart_config
                    if 'data' in chart_config:
                        fig = None
                        if chart_config['chart_type'] == "Bar":
                            fig = px.bar(chart_config['data'], x=chart_config['x_column'], y=chart_config['y_column'], color=chart_config['color_column'])
                        elif chart_config['chart_type'] == "Line":
                            fig = px.line(chart_config['data'], x=chart_config['x_column'], y=chart_config['y_column'], color=chart_config['color_column'])
                        elif chart_config['chart_type'] == "Scatter":
                            fig = px.scatter(chart_config['data'], x=chart_config['x_column'], y=chart_config['y_column'], color=chart_config['color_column'])
                        elif chart_config['chart_type'] == "Pie":
                            fig = px.pie(chart_config['data'], names=chart_config['x_column'], values=chart_config['y_column'])
                        
                        # Render the chart if the figure is created
                        if fig:
                            st.plotly_chart(fig)
                    else:
                        st.warning(f"No data found for chart: {chart_config['chart_title']}")
                
                chart_count += 1

def main():
    st.title("Dashboard Viewer")

    client = get_mongo_client()
    
    # Select a dashboard to view
    dashboards = get_all_dashboards(client)
    if dashboards:
        dashboard_names = [dashboard['dashboard_name'] for dashboard in dashboards]
        selected_dashboard = st.selectbox("Select a Dashboard", dashboard_names)
        
        if selected_dashboard:
            render_dashboard(client, selected_dashboard)

if __name__ == "__main__":
    main()
