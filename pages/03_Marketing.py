import logging
import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levellevel)s - %(message)s", 
    level=logging.DEBUG
)

def get_mongo_client():
    try:
        logging.debug("Attempting to connect to MongoDB...")
        connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
        client = MongoClient(connection_string, 
                     ssl=True,
                     serverSelectionTimeoutMS=30000,
                     connectTimeoutMS=30000,
                     socketTimeoutMS=30000)
        logging.info("MongoDB connection successful")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise

def get_collection_data(client, collection_name):
    try:
        logging.debug(f"Fetching data from collection: {collection_name}")
        db = client['netsuite']  # Ensure the database name is correct
        collection = db[collection_name]
        
        data = []
        for doc in collection.find():
            try:
                # Process each document individually
                processed_doc = {}
                for key, value in doc.items():
                    if isinstance(value, str):
                        processed_doc[key] = value.encode('utf-8', 'ignore').decode('utf-8')
                    else:
                        processed_doc[key] = value
                data.append(processed_doc)
            except Exception as e:
                logging.error(f"Skipping problematic document {doc.get('_id', 'Unknown ID')}: {e}")
                continue  # Skip problematic document
        
        df = pd.DataFrame(data)
        logging.info(f"Data fetched successfully from {collection_name} with shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Error fetching data from collection {collection_name}: {e}")
        raise

def apply_filters(df):
    # Check and apply date filter only if a valid 'Date' column is present
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        if not df.empty:  # Check if there are valid date entries left
            min_date = df['Date'].min()
            max_date = df['Date'].max()

            start_date, end_date = st.date_input(
                "Select date range:",
                value=[min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
            df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

    # Filter by Numeric Columns
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_columns:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        selected_range = st.slider(f"Filter by {col}:", min_val, max_val, (min_val, max_val))
        df = df[(df[col] >= selected_range[0]) & (df[col] <= selected_range[1])]

    # Filter by Categorical Columns
    categorical_columns = df.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        unique_values = df[col].unique().tolist()
        selected_values = st.multiselect(f"Filter by {col}:", unique_values, default=unique_values)
        df = df[df[col].isin(selected_values)]
    
    return df

def create_visualizations(df):
    st.subheader("Create Your Own Visualizations")

    # Select columns for X and Y axes
    x_column = st.selectbox("Select X-axis column", df.columns)
    y_column = st.selectbox("Select Y-axis column", df.columns)

    # Select the type of chart
    chart_type = st.selectbox("Select chart type", ["Bar", "Line", "Scatter", "Histogram"])

    # Create the chart based on user input
    if chart_type == "Bar":
        fig = px.bar(df, x=x_column, y=y_column)
    elif chart_type == "Line":
        fig = px.line(df, x=x_column, y=y_column)
    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x_column, y=y_column)
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x_column)

    # Display the chart
    st.plotly_chart(fig)

def main():
    st.title("MongoDB Data Visualization Tool")

    # Connect to MongoDB using the utility function
    client = get_mongo_client()

    # Specify the collection to display (in this case, always 'sales')
    collection_name = "sales"

    # Load the entire collection into a DataFrame
    data = get_collection_data(client, collection_name)

    # Apply filters to the data
    filtered_data = apply_filters(data)

    # Check if DataFrame is empty after filtering
    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        st.write(f"Filtered DataFrame: {filtered_data.shape[0]} rows")
        st.dataframe(filtered_data)

        # Call the visualization function
        create_visualizations(filtered_data)

if __name__ == "__main__":
    main()
