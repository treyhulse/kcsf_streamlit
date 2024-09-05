import streamlit as st
import pandas as pd
import calendar
from pymongo import MongoClient
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Shipping Calendar",
    layout="wide",
    initial_sidebar_state="expanded",
)

# MongoDB connection with increased timeout values
def get_mongo_client():
    connection_string = st.secrets["mongo_connection_string"] + "?retryWrites=true&w=majority"
    client = MongoClient(connection_string, ssl=True, serverSelectionTimeoutMS=60000, connectTimeoutMS=60000, socketTimeoutMS=60000)
    return client

# Cache the data loaded from MongoDB to improve speed
@st.cache_data
def load_shipping_data(batch_size=100):
    client = get_mongo_client()
    db = client['netsuite']
    collection = db['sales']  # Assuming 'sales' collection has shipping data

    data = []
    cursor = collection.find({}).batch_size(batch_size)

    for doc in cursor:
        if 'Ship Date (Admin)' in doc:
            doc['Ship Date (Admin)'] = pd.to_datetime(doc['Ship Date (Admin)'], errors='coerce')
        data.append(doc)

    df = pd.DataFrame(data)
    
    # Drop the '_id' column if it exists
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    
    return df

# Group data by ship_date and ship_via, sum the quantity
def aggregate_data(df):
    return df.groupby(['Ship Date (Admin)', 'Ship Via']).sum().reset_index()

# Main function
def main():
    st.title("Shipping Calendar")

    # Load shipping data
    df = load_shipping_data()

    if not df.empty:
        df_aggregated = aggregate_data(df)

        # Get current date and range of next 3-4 weeks
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=3)

        # Create a date range for the next 3-4 weeks (only weekdays)
        weekdays = pd.date_range(start=start_date, end=end_date, freq='B')

        # Create a calendar-like layout with 5 columns (Monday to Friday)
        week_number = 0
        for i in range(0, len(weekdays), 5):
            cols = st.columns(5)
            for j, date in enumerate(weekdays[i:i + 5]):
                if date in df_aggregated['ship_date'].values:
                    day_data = df_aggregated[df_aggregated['ship_date'] == date]
                    cols[j].markdown(f"### **{date.strftime('%Y-%m-%d')}**")
                    for _, row in day_data.iterrows():
                        cols[j].write(f"{row['ship_via']}: {row['qty']} units")
                else:
                    cols[j].markdown(f"### **{date.strftime('%Y-%m-%d')}**")
                    cols[j].write("No shipments")

if __name__ == "__main__":
    main()
