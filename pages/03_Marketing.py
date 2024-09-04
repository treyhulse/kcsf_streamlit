import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
import logging
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from utils.mongo_connection import get_mongo_client  # Ensure this is correctly referenced

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

# Capture the user's email and validate access
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

page_name = '03_Marketing.py'
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

# Function to get paginated data from MongoDB
def get_paginated_data(client, collection_name, batch_size=100):
    db = client['netsuite']
    collection = db[collection_name]

    data = []
    total_docs = collection.estimated_document_count()
    progress_bar = st.progress(0)

    for i, doc in enumerate(collection.find().batch_size(batch_size)):
        processed_doc = {key: value for key, value in doc.items()}
        data.append(processed_doc)
        progress_bar.progress((i + 1) / total_docs)

    df = pd.DataFrame(data)
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)

    return df

# Function to create visualizations
def create_visualizations(df):
    st.subheader("Create Your Own Visualizations")
    
    # Select columns for X and Y axes
    x_column = st.selectbox("Select X-axis column", df.columns, index=df.columns.get_loc("Date"))
    y_column = st.selectbox("Select Y-axis column", df.columns, index=df.columns.get_loc("Amount"))
    chart_type = st.selectbox("Select chart type", ["Bar", "Line", "Scatter", "Pie"])
    
    if chart_type == "Bar":
        fig = px.bar(df, x=x_column, y=y_column)
    elif chart_type == "Line":
        fig = px.line(df, x=x_column, y=y_column)
    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x_column, y=y_column)
    elif chart_type == "Pie":
        fig = px.pie(df, names=x_column, values=y_column)
    
    st.plotly_chart(fig)

# Main function
def main():
    client = get_mongo_client()
    df = get_paginated_data(client, 'sales')  # Load the data with pagination
    
    if df.empty:
        st.warning("No data available")
    else:
        create_visualizations(df)  # Create visualizations with the data
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        grid_options = gb.build()
        AgGrid(df, gridOptions=grid_options)

if __name__ == "__main__":
    main()
