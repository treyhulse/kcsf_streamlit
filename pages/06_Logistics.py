import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set page layout to wide
st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '06_Logistics.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta

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
            doc['Ship Date (Admin)'] = pd.to_datetime(doc['Ship Date (Admin)'], errors='coerce').normalize()
        data.append(doc)

    df = pd.DataFrame(data)
    
    # Drop the '_id' column if it exists
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    
    return df

# Group data by 'Ship Date (Admin)' and 'Ship Via', counting rows instead of summing quantities
def aggregate_data(df):
    return df.groupby(['Ship Date (Admin)', 'Ship Via']).size().reset_index(name='order_count')

# Custom date picker for "This Week", "Next Week", "This Month", "Next Month", and custom range
def get_date_range():
    option = st.selectbox(
        "Select Date Range",
        ["Custom Range", "This Week", "Next Week", "This Month", "Next Month"],
        index=3  # Set 'This Month' as the default selected option (index starts at 0)
    )

    today = datetime.today().date()  # Work with date instead of datetime
    if option == "This Week":
        start_date = today - timedelta(days=today.weekday())  # Start of the current week (Monday)
        end_date = start_date + timedelta(days=4)  # End of the current week (Friday)
    elif option == "Next Week":
        start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=1)  # Start of next week (Monday)
        end_date = start_date + timedelta(days=4)  # End of next week (Friday)
    elif option == "This Month":
        start_date = today.replace(day=1)  # First day of the current month
        next_month = (start_date + timedelta(days=32)).replace(day=1)  # First day of the next month
        end_date = next_month - timedelta(days=1)  # Last day of the current month
    elif option == "Next Month":
        start_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1)  # First day of the next month
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # Last day of the next month
    else:
        # Custom range with date input
        start_date = st.date_input("Start Date", value=today)
        end_date = st.date_input("End Date", value=today + timedelta(days=7))

    return start_date, end_date

# Skip weekends (Saturday and Sunday)
def filter_weekdays(date_range):
    return [date for date in date_range if date.weekday() < 5]  # 0 = Monday, 4 = Friday

# Main function
def main():
    st.title("Shipping Calendar")

    # Load shipping data
    df = load_shipping_data()

    if not df.empty:
        df_aggregated = aggregate_data(df)

        # Get unique 'Ship Via' values for filtering
        all_ship_vias = df_aggregated['Ship Via'].unique().tolist()
        selected_ship_vias = st.multiselect("Select Ship Via", options=['All'] + all_ship_vias, default='Our Truck')

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

        # Create a list of weekdays to display (max 15 days)
        date_range = pd.date_range(start=start_date, end=end_date).normalize()
        date_range = filter_weekdays(date_range)  # Skip weekends

        if len(date_range) > 15:
            date_range = date_range[:15]

        # Create a 5-column layout for the calendar with improved cards for each day
        for i in range(0, len(date_range), 5):
            cols = st.columns(5)
            for j, date in enumerate(date_range[i:i + 5]):
                with cols[j]:
                    day_data = filtered_df[filtered_df['Ship Date (Admin)'] == date]

                    # Generate the list of ship vias and their corresponding order counts
                    if not day_data.empty:
                        order_summary = ""
                        for _, row in day_data.iterrows():
                            order_summary += f"{row['Ship Via']}: {row['order_count']} orders<br>"

                    st.markdown(
                        f"""
                        <div style='border: 2px solid #ddd; border-radius: 10px; padding: 20px; background-color: #f9f9f9;
                                    box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align: center; height: auto;'>
                            <h3 style='margin-bottom: 10px;'>{date.strftime('%Y-%m-%d')}</h3>
                            <p style='font-size: 18px; color: #666;'>{order_summary if day_data.empty == False else "No shipments"}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    main()
