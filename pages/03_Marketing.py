import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection (not cached)
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000, socketTimeoutMS=30000)
    return client

# Cache only the data, not the MongoDB client
@st.cache_data
def load_data(collection_name):
    client = get_mongo_client()  # Create MongoClient inside the function
    db = client['netsuite']
    collection = db[collection_name]
    data = pd.DataFrame(list(collection.find()))
    
    if '_id' in data.columns:
        data.drop(columns=['_id'], inplace=True)
    
    return data

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

# Function to apply global filters
def apply_filters(df):
    st.sidebar.header("Global Filters")

    # Date range filter
    start_date = st.sidebar.date_input("Start Date", df['Date'].min().date())
    end_date = st.sidebar.date_input("End Date", df['Date'].max().date())

    # Filter by Type with 'All' option
    types = ['All'] + df['Type'].unique().tolist()
    selected_types = st.sidebar.multiselect("Filter by Type", types, default='All')
    
    # Filter by Status with 'All' option
    statuses = ['All'] + df['Status'].unique().tolist()
    selected_statuses = st.sidebar.multiselect("Filter by Status", statuses, default='All')

    # Apply Date Filter
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    # Apply Type Filter
    if 'All' not in selected_types:
        df = df[df['Type'].isin(selected_types)]
    
    # Apply Status Filter
    if 'All' not in selected_statuses:
        df = df[df['Status'].isin(selected_statuses)]
    
    return df

# Main function
@st.cache_data
def main():
    # Load and cache the data from 'salesLines'
    df = load_data('salesLines')

    # Apply global filters
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
                        "collection_name": "salesLines",
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
