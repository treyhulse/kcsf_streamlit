import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Shipping Report'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import streamlit as st
import time
import requests
from requests_oauthlib import OAuth1
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth1 Authentication setup for NetSuite
def get_authentication():
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

# Function to fetch JSON data from RESTlet and convert it to a DataFrame
def fetch_restlet_data(saved_search_id):
    url = f"{st.secrets['url_restlet']}&savedSearchId={saved_search_id}"
    auth = get_authentication()
    
    try:
        logger.info(f"Fetching data from: {url}")
        response = requests.get(url, auth=auth, headers={"Content-Type": "application/json"})
        response.raise_for_status()

        # Assuming the response is JSON, turn it into a DataFrame
        data = response.json()

        if not data or len(data) == 0:
            logger.info("No data returned.")
            return pd.DataFrame()  # Return empty DataFrame if no data

        # Convert list of dictionaries into a DataFrame
        df = pd.DataFrame(data)
        return df

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# Main function
def main():
    # Define tabs
    tab1, tab2 = st.tabs(["Shipping Report", "Shipping Calendar"])

    # Tab 1: Open Sales Orders Analysis
    with tab1:
        st.header("Shipping Report")
        
        # Fetch Data using the new RESTlet method
        with st.spinner("Fetching Open Sales Orders..."):
            df_open_so = fetch_restlet_data("customsearch5065")

        # Display charts
        if not df_open_so.empty:
            col_chart, col_pie = st.columns([2, 1])

            # Line Chart: Open Sales Orders by Ship Date
            with col_chart:
                df_open_so['Ship Date'] = pd.to_datetime(df_open_so['Ship Date'])
                ship_date_counts = df_open_so['Ship Date'].value_counts().sort_index()
                fig = px.line(x=ship_date_counts.index, y=ship_date_counts.values, labels={'x': 'Ship Date', 'y': 'Number of Orders'}, title='Open Sales Orders by Ship Date')
                st.plotly_chart(fig, use_container_width=True)

            # Pie Chart: Tasked vs Untasked Orders
            with col_pie:
                matched_orders = df_open_so['Task ID'].notna().sum()
                unmatched_orders = df_open_so['Task ID'].isna().sum()
                pie_data = pd.DataFrame({'Task Status': ['Tasked Orders', 'Untasked Orders'], 'Count': [matched_orders, unmatched_orders]})
                fig = px.pie(pie_data, names='Task Status', values='Count', title='Tasked vs Untasked Orders', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the selected filters.")

        # Display metrics and data
        total_orders = len(df_open_so)
        matched_orders = df_open_so['Task ID'].notna().sum()
        unmatched_orders = df_open_so['Task ID'].isna().sum()
        successful_task_percentage = (matched_orders / total_orders) * 100 if total_orders > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Open Orders", total_orders)
        with col2:
            st.metric("Tasked Orders", matched_orders)
        with col3:
            st.metric("Untasked Orders", unmatched_orders)
        with col4:
            st.metric("Successful Task Percentage", f"{successful_task_percentage:.2f}%")

        # Data table and download option
        with st.expander("View Data Table"):
            st.write(f"Total records after filtering: {len(df_open_so)}")
            st.dataframe(df_open_so, height=400)
            csv = df_open_so.to_csv(index=False)
            st.download_button(label="Download filtered data as CSV", data=csv, file_name="filtered_sales_orders.csv", mime="text/csv")

    # Tab 2: Shipping Calendar
    with tab2:
        st.header("Shipping Calendar")
        progress = st.progress(0)

        with st.spinner("Initializing..."):
            time.sleep(0.5)

        for i in range(1, 6):
            time.sleep(0.3)
            progress.progress(i * 20)

        df = fetch_restlet_data("customsearch5065")

        if not df.empty:
            df['Ship Date'] = pd.to_datetime(df['Ship Date']).dt.strftime('%m/%d/%Y')

            # Display Ship Via and Date Range filters in two columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Select Ship Via")
                ship_vias = ['All'] + df['Ship Via'].unique().tolist()
                selected_ship_vias = st.multiselect("Ship Via", ship_vias, default=['All'])

                if 'All' in selected_ship_vias:
                    selected_ship_vias = df['Ship Via'].unique().tolist()

            with col2:
                st.subheader("Select Date Range")
                start_date, end_date = date.today(), date.today() + timedelta(days=30)
            
            # Apply filters
            df_filtered = df[
                (df['Ship Via'].isin(selected_ship_vias)) & 
                (pd.to_datetime(df['Ship Date']) >= pd.to_datetime(start_date)) & 
                (pd.to_datetime(df['Ship Date']) <= pd.to_datetime(end_date))
            ]

            # Group by Ship Date and Ship Via
            grouped = df_filtered.groupby(['Ship Date', 'Ship Via']).size().reset_index(name='Total Orders')

            # Create 5 vertical columns (Monday through Friday)
            cols = st.columns(5)
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            days = pd.date_range(start=start_date, end=end_date, freq='B').strftime('%m/%d/%Y')

            # Display by weekday
            for i, day_name in enumerate(weekdays):
                with cols[i]:
                    st.subheader(day_name)

                    for date_str in days:
                        date_obj = pd.to_datetime(date_str)
                        if date_obj.weekday() == i:
                            orders_today = df_filtered[df_filtered['Ship Date'] == date_str]

                            if not orders_today.empty:
                                total_orders = len(orders_today)
                                with st.expander(f"{date_str} - Total Orders: {total_orders}"):
                                    st.dataframe(orders_today)
                            else:
                                with st.expander(f"{date_str} - No shipments"):
                                    st.write("No orders for this day.")
        else:
            st.write("No data available for the selected filters.")

if __name__ == "__main__":
    main()
