import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection with increased timeout values
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
    return client

# Cache the data loaded from MongoDB to improve speed
@st.cache_data
def load_filtered_data(collection_name, batch_size=100):
    client = get_mongo_client()
    db = client['netsuite']
    collection = db[collection_name]
    
    # Remove the date filter, load all data
    data = []
    progress_bar = st.progress(0)
    
    total_docs = collection.count_documents({})  # Count all documents
    cursor = collection.find({}).batch_size(batch_size)  # Fetch all documents without filtering

    for i, doc in enumerate(cursor):
        # Convert 'Date' field to a datetime object if it's a string
        if 'Date' in doc:
            doc['Date'] = pd.to_datetime(doc['Date'], errors='coerce')
        data.append(doc)
        progress_bar.progress((i + 1) / total_docs)  # Update progress bar

    df = pd.DataFrame(data)
    
    # Drop the '_id' column
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    
    return df

# Save the visualization criteria to MongoDB
def save_chart(client, user_email, chart_config):
    db = client['netsuite']
    charts_collection = db['charts']
    
    chart_data = {
        "user": user_email,
        "chart_config": chart_config,
        "created_at": datetime.utcnow()
    }
    charts_collection.insert_one(chart_data)
    st.success("Chart configuration saved successfully!")

# Function to capture user email from st.experimental_user
def capture_user_email():
    user_info = st.experimental_user
    if user_info:
        return user_info.get('email')
    return None

# Function to apply additional filters after pre-applied ones
def apply_filters(df):
    st.sidebar.header("Global Filters")

    # Filter by Type with 'All' option
    selected_types = []
    if 'Type' in df.columns:
        types = ['All'] + df['Type'].unique().tolist()
        selected_types = st.sidebar.multiselect("Filter by Type", types, default='All')
        
        # Apply Type Filter
        if 'All' not in selected_types:
            df = df[df['Type'].isin(selected_types)]
    else:
        st.warning("The 'Type' column is missing from the data.")

    # Filter by Status with 'All' option (default 'Billed')
    selected_statuses = []
    if 'Status' in df.columns:
        statuses = ['All'] + df['Status'].unique().tolist()
        selected_statuses = st.sidebar.multiselect("Filter by Status", statuses, default=['Billed'])
        
        # Apply Status Filter
        if 'All' not in selected_statuses:
            df = df[df['Status'].isin(selected_statuses)]
    else:
        st.warning("The 'Status' column is missing from the data.")
    
    return df, selected_types, selected_statuses

# Main function
def main():
    st.title("Sales Dashboard")

    # Load filtered data using cached data
    df = load_filtered_data('salesLines')  # Now using 'sales' collection

    # Apply additional filters
    if not df.empty:
        df_filtered, selected_types, selected_statuses = apply_filters(df)
    else:
        st.warning("No data was returned from the database.")

    # Expandable section to view first 10 rows of the filtered dataframe
    if not df_filtered.empty:
        with st.expander("View First 10 Rows of Filtered Data"):
            st.dataframe(df_filtered.head(10))
    else:
        st.warning("No data available after filtering.")

    # Form for selecting visualization options
    st.subheader("Create Custom Visualization")

    with st.form(key='visualization_form'):
        # X-axis and Y-axis selection
        x_column = st.selectbox("Select X-axis", df_filtered.columns)
        y_column = st.selectbox("Select Y-axis", df_filtered.columns)
        
        # Color by selection
        color_column = st.selectbox("Color By", [None] + list(df_filtered.columns), index=0)
        
        # Chart type selection
        chart_type = st.selectbox("Select Chart Type", ["Bar", "Line", "Scatter", "Pie"])
        
        # Submit button for preview and saving the chart
        submit_button = st.form_submit_button(label="Preview and Save Chart")
        
        # If the button is clicked, render the chart and save it
        if submit_button:
            # Create visualization based on user input
            fig = None
            if chart_type == "Bar":
                fig = px.bar(df_filtered, x=x_column, y=y_column, color=color_column)
            elif chart_type == "Line":
                fig = px.line(df_filtered, x=x_column, y=y_column, color=color_column)
            elif chart_type == "Scatter":
                fig = px.scatter(df_filtered, x=x_column, y=y_column, color=color_column)
            elif chart_type == "Pie":
                fig = px.pie(df_filtered, names=x_column, values=y_column)
            
            # Display the chart
            if fig:
                st.plotly_chart(fig)
                
                # Get the Mongo client
                client = get_mongo_client()

                # Save the chart configuration
                user_email = capture_user_email()  # Get the user email using the capture_user_email function
                if user_email:
                    chart_config = {
                        "collection_name": "salesLines",
                        "x_column": x_column,
                        "y_column": y_column,
                        "color_column": color_column,
                        "chart_type": chart_type,
                        "selected_types": selected_types,
                        "selected_statuses": selected_statuses,
                        "chart_title": f"{chart_type} Chart of {y_column} vs {x_column}"
                    }
                    save_chart(client, user_email, chart_config)
                else:
                    st.error("Unable to capture user email.")

if __name__ == "__main__":
    main()
