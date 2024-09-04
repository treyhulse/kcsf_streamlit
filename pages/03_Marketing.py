import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000, socketTimeoutMS=30000)
    return client

# Function to get paginated data from MongoDB
def get_paginated_data(client, collection_name, limit=10):
    db = client['netsuite']
    collection = db[collection_name]
    data = pd.DataFrame(list(collection.find().limit(limit)))
    
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

# Main function
def main():
    client = get_mongo_client()
    
    # Load the first 10 rows of the 'salesLines' collection
    df = get_paginated_data(client, 'salesLines', limit=10)

    # Expandable section to view the first 10 rows of the dataframe
    with st.expander("View First 10 Rows of Data"):
        st.dataframe(df)

    # Form for selecting visualization options
    st.subheader("Create Custom Visualization")

    with st.form(key='visualization_form'):
        # X-axis and Y-axis selection
        x_column = st.selectbox("Select X-axis", df.columns)
        y_column = st.selectbox("Select Y-axis", df.columns)
        
        # Color by selection
        color_column = st.selectbox("Color By", [None] + list(df.columns), index=0)
        
        # Chart type selection
        chart_type = st.selectbox("Select Chart Type", ["Bar", "Line", "Scatter", "Pie"])
        
        # Submit button for preview
        submit_button = st.form_submit_button(label="Preview")
        
        # If the button is clicked, render the chart
        if submit_button:
            # Create visualization based on user input
            fig = None
            if chart_type == "Bar":
                fig = px.bar(df, x=x_column, y=y_column, color=color_column)
            elif chart_type == "Line":
                fig = px.line(df, x=x_column, y=y_column, color=color_column)
            elif chart_type == "Scatter":
                fig = px.scatter(df, x=x_column, y=y_column, color=color_column)
            elif chart_type == "Pie":
                fig = px.pie(df, names=x_column, values=y_column)
            
            # Display the chart
            if fig:
                st.plotly_chart(fig)
            
            # Save chart configuration option
            if st.button("Save Chart"):
                user_email = st.secrets["user_email"]  # Assuming user email is in secrets
                chart_config = {
                    "x_column": x_column,
                    "y_column": y_column,
                    "color_column": color_column,
                    "chart_type": chart_type,
                    "chart_title": f"{chart_type} Chart of {y_column} vs {x_column}"
                }
                save_chart(client, user_email, chart_config)

if __name__ == "__main__":
    main()
