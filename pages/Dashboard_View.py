import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Dashboard View'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################


import plotly.express as px
from pymongo import MongoClient
import pandas as pd

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

# Fetch the data for the chart from the appropriate collection
def get_chart_data(client, collection_name, filters=None):
    db = client['netsuite']
    collection = db[collection_name]
    
    # Apply filters if provided, otherwise fetch all data
    data = collection.find(filters if filters else {})
    
    # Convert to DataFrame
    df = pd.DataFrame(list(data))
    
    # Drop the '_id' column if it exists
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    
    return df

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
                    
                    # Fetch data for the chart from the specified collection (e.g., 'sales')
                    collection_name = chart_config['collection_name']
                    filters = {}  # Define any filters based on the chart config, e.g., date range, status, etc.
                    
                    # Pull the data dynamically based on chart config
                    df = get_chart_data(client, collection_name, filters)
                    
                    # Check if the DataFrame has data
                    if not df.empty:
                        # Create a chart based on its saved configuration
                        fig = None
                        if chart_config['chart_type'] == "Bar":
                            fig = px.bar(df, x=chart_config['x_column'], y=chart_config['y_column'], color=chart_config['color_column'])
                        elif chart_config['chart_type'] == "Line":
                            fig = px.line(df, x=chart_config['x_column'], y=chart_config['y_column'], color=chart_config['color_column'])
                        elif chart_config['chart_type'] == "Scatter":
                            fig = px.scatter(df, x=chart_config['x_column'], y=chart_config['y_column'], color=chart_config['color_column'])
                        elif chart_config['chart_type'] == "Pie":
                            fig = px.pie(df, names=chart_config['x_column'], values=chart_config['y_column'])
                        
                        # Render the chart
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
