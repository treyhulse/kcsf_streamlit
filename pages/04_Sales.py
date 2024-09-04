import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '04_Sales.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import logging
from pymongo import MongoClient
import pandas as pd
import streamlit as st

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

# Import mongo connection function
from mongo_connection import get_mongo_client

# Pagination function to load large datasets
def get_paginated_data(client, collection_name, batch_size=100):
    db = client['netsuite']
    collection = db[collection_name]

    data = []
    total_docs = collection.estimated_document_count()
    progress_bar = st.progress(0)

    # Fetching documents in batches for better performance
    for i, doc in enumerate(collection.find().batch_size(batch_size)):
        processed_doc = {key: value for key, value in doc.items()}
        data.append(processed_doc)
        progress_bar.progress((i + 1) / total_docs)

    df = pd.DataFrame(data)

    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)

    return df

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
                fig = px.bar(df, x=chart['x_column'], y=chart['y_column'], color=chart['color_column'], 
                             title=chart['chart_title'], labels={chart['x_column']: chart['x_label'], 
                             chart['y_column']: chart['y_label']})
            elif chart['type'] == "Line":
                fig = px.line(df, x=chart['x_column'], y=chart['y_column'], color=chart['color_column'], 
                              title=chart['chart_title'], labels={chart['x_column']: chart['x_label'], 
                              chart['y_column']: chart['y_label']})
            if fig:
                st.plotly_chart(fig)

def main():
    client = get_mongo_client()
    df = get_paginated_data(client, 'salesLines')  # Load the data with pagination
    display_selected_charts(client, df, "04_Sales")

if __name__ == "__main__":
    main()
