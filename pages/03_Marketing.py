import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB connection with increased timeout values
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
    return client

# Function to apply default filters (This Month, Billed status) when loading data
def load_filtered_data(collection_name, batch_size=100):
    client = get_mongo_client()
    db = client['netsuite']
    collection = db[collection_name]
    
    # Default filter: This Month's data
    today = datetime.today()
    first_day_of_month = today.replace(day=1)
    
    # Query to filter by date (This Month) and status (Billed)
    query = {
        "Status": "Billed"
    }
    
    data = []
    progress_bar = st.progress(0)
    
    total_docs = collection.count_documents(query)  # Get the total number of documents
    cursor = collection.find(query).batch_size(batch_size)  # Use batch_size to control data loading

    for i, doc in enumerate(cursor):
        # Convert 'Date' field to a datetime object if it's a string
        if 'Date' in doc:
            doc['Date'] = pd.to_datetime(doc['Date'], errors='coerce')
        data.append(doc)
        progress_bar.progress((i + 1) / total_docs)  # Update progress bar

    df = pd.DataFrame(data)
    
    # Drop the '_id' column and handle missing columns like 'Date'
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    
    return df

# Save visualization config to MongoDB
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

# Function to apply additional filters after pre-applied ones
def apply_filters(df):
    st.sidebar.header("Global Filters")

    # Date range filter (still allow users to change it from This Month)
    start_date = st.sidebar.date_input("Start Date", df['Date'].min().date())
    end_date = st.sidebar.date_input("End Date", df['Date'].max().date())

    # Filter by Type with 'All' option
    types = ['All'] + df['Type'].unique().tolist()
    selected_types = st.sidebar.multiselect("Filter by Type", types, default='All')
    
    # Filter by Status with 'All' option (default 'Billed')
    statuses = ['All'] + df['Status'].unique().tolist()
    selected_statuses = st.sidebar.multiselect("Filter by Status", statuses, default=['Billed'])

    # Apply Date Filter
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    # Apply Type Filter
    if 'All' not in selected_types:
        df = df[df['Type'].isin(selected_types)]
    
    # Apply Status Filter
    if 'All' not in selected_statuses:
        df = df[df['Status'].isin(selected_statuses)]
    
    return df

# Main function
def main():
    st.title("Marketing Dashboard")

    # Load filtered data by default (This Month, Billed status)
    df = load_filtered_data('sales')  # Now using 'sales' collection

    # Apply additional filters
    df_filtered = apply_filters(df)

    # Expandable section to view first 10 rows of the filtered dataframe
    with st.expander("View First 10 Rows of Filtered Data"):
        st.dataframe(df_filtered.head(10))

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
        
        # Submit button for preview
        submit_button = st.form_submit_button(label="Preview")
        
        # If the button is clicked, render the chart
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
                
                # Move Save Chart button to show after chart preview
                if st.button("Save Chart"):
                    user_email = st.secrets["user_email"]  # Assuming user email is in secrets
                    chart_config = {
                        "collection_name": "sales",
                        "x_column": x_column,
                        "y_column": y_column,
                        "color_column": color_column,
                        "chart_type": chart_type,
                        "start_date": str(df_filtered['Date'].min()),
                        "end_date": str(df_filtered['Date'].max()),
                        "selected_types": selected_types,
                        "selected_statuses": selected_statuses,
                        "chart_title": f"{chart_type} Chart of {y_column} vs {x_column}"
                    }
                    save_chart(client, user_email, chart_config)

if __name__ == "__main__":
    main()
