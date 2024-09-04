import logging
from pymongo import MongoClient
import pandas as pd
import streamlit as st
import plotly.express as px
from utils.mongo_connection import get_mongo_client  # Ensure this is correctly referenced

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

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

# Function to display charts
def display_selected_charts(client, df, page_name):
    st.title(f"{page_name}")

    db = client['netsuite']
    pages_collection = db['pages']
    page_config = pages_collection.find_one({"page_name": page_name})

    if not page_config or not page_config.get("selected_charts"):
        st.warning(f"No charts configured for {page_name}.")
        return

    saved_visualizations = list(db['charts'].find())
    selected_charts = page_config['selected_charts']

    for chart_name in selected_charts:
        chart = next((viz for viz in saved_visualizations if viz['name'] == chart_name), None)
        if chart:
            st.subheader(chart['chart_title'])
            fig = None
            if chart['type'] == "Bar":
                fig = px.bar(df, x=chart['x_column'], y=chart['y_column'], color=chart['color_column'])
            elif chart['type'] == "Line":
                fig = px.line(df, x=chart['x_column'], y=chart['y_column'], color=chart['color_column'])
            if fig:
                st.plotly_chart(fig)

# Main function
def main():
    client = get_mongo_client()
    df = get_paginated_data(client, 'salesLines')  # Load the data with pagination
    display_selected_charts(client, df, "04_Sales")

if __name__ == "__main__":
    main()
