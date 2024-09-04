import streamlit as st
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
