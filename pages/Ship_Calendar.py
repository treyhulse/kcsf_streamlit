import streamlit as st
import pandas as pd
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

# Group data by 'Ship Date (Admin)' and 'Ship Via', counting rows instead of summing quantities
def aggregate_data(df):
    return df.groupby(['Ship Date (Admin)', 'Ship Via']).size().reset_index(name='order_count')

# Custom date picker for "This Week", "Next Week", "This Month", and custom range
def get_date_range():
    option = st.selectbox(
        "Select Date Range",
        ["Custom Range", "This Week", "Next Week", "This Month"]
    )

    today = datetime.today()
    if option == "This Week":
        start_date = today - timedelta(days=today.weekday())  # Start of the current week (Monday)
        end_date = start_date + timedelta(days=6)  # End of the current week (Sunday)
    elif option == "Next Week":
        start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=1)  # Start of next week (Monday)
        end_date = start_date + timedelta(days=6)  # End of next week (Sunday)
    elif option == "This Month":
        start_date = today.replace(day=1)  # First day of the current month
        next_month = today.replace(day=28) + timedelta(days=4)  # Move to the next month
        end_date = next_month.replace(day=1) - timedelta(days=1)  # Last day of the current month
    else:
        # Custom range with date input
        start_date = st.date_input("Start Date", value=today)
        end_date = st.date_input("End Date", value=today + timedelta(days=7))

    return start_date, end_date

# Main function
def main():
    st.title("Shipping Calendar")

    # Load shipping data
    df = load_shipping_data()

    if not df.empty:
        df_aggregated = aggregate_data(df)

        # Get unique 'Ship Via' values for filtering
        all_ship_vias = df_aggregated['Ship Via'].unique().tolist()
        selected_ship_vias = st.multiselect("Select Ship Via", options=['All'] + all_ship_vias, default='All')

        # Apply 'Ship Via' filter (if 'All' is selected, include all)
        if 'All' not in selected_ship_vias:
            df_aggregated = df_aggregated[df_aggregated['Ship Via'].isin(selected_ship_vias)]

        # Get the date range using custom date picker
        start_date, end_date = get_date_range()

        # Filter data to the selected date range
        filtered_df = df_aggregated[
            (df_aggregated['Ship Date (Admin)'] >= pd.to_datetime(start_date)) &
            (df_aggregated['Ship Date (Admin)'] <= pd.to_datetime(end_date))
        ]

        # Create a list of dates to display (max 15 days)
        date_range = pd.date_range(start=start_date, end=end_date)
        if len(date_range) > 15:
            date_range = date_range[:15]

        # Create a 5-column layout for the calendar with cards for each day
        for i in range(0, len(date_range), 5):
            cols = st.columns(5)
            for j, date in enumerate(date_range[i:i + 5]):
                with cols[j]:
                    st.markdown(f"### **{date.strftime('%Y-%m-%d')}**")
                    day_data = filtered_df[filtered_df['Ship Date (Admin)'] == date]

                    # Add a card-style layout for each day
                    if not day_data.empty:
                        st.markdown(
                            """
                            <div style='border:1px solid #ddd; border-radius:10px; padding:10px; background-color:#f9f9f9;'>
                            """, unsafe_allow_html=True)
                        
                        # Create a small table for the day's data
                        st.table(day_data[['Ship Via', 'order_count']].set_index('Ship Via'))
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.write("No shipments")

if __name__ == "__main__":
    main()
