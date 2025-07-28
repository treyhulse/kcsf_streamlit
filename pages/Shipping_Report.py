"""
KCSF Shipping Report Dashboard

This Streamlit page provides a comprehensive shipping data analysis dashboard.
It fetches data from NetSuite RESTlets and presents it with interactive filters
and visualizations for shipping operations management.

Data Sources:
- Open Orders (customsearch5190)
- Pick Tasks (customsearch5457) 
- Our Truck Orders (customsearch5147)

Author: KCSF Development Team
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.restlet import fetch_restlet_data
import plotly.express as px

# Page Configuration
st.title("Shipping Report")

# =============================================================================
# DATA FETCHING AND CACHING
# =============================================================================

@st.cache_data(ttl=120)
def fetch_raw_data(saved_search_id):
    """
    Fetch raw data from NetSuite RESTlet with caching.
    
    Args:
        saved_search_id (str): NetSuite saved search ID
        
    Returns:
        pd.DataFrame: Fetched data as pandas DataFrame
    """
    return fetch_restlet_data(saved_search_id)

# Fetch all required datasets
open_order_data = fetch_raw_data("customsearch5190")  # Open orders with ship dates
pick_task_data = fetch_raw_data("customsearch5457")   # Pick task assignments
our_truck_data = fetch_raw_data("customsearch5147")   # Our truck delivery orders

# =============================================================================
# DATA PROCESSING
# =============================================================================

# Extract only required columns from pick task data
pick_task_data = pick_task_data[['Order Number', 'Task ID']]

# Merge open orders with pick task data
merged_df = pd.merge(open_order_data, pick_task_data, on='Order Number', how='left')

# Convert ship date to datetime for proper filtering
merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'], errors='coerce')

# =============================================================================
# SIDEBAR FILTERS
# =============================================================================

st.sidebar.header('Filters')

# Sales Representative Filter
sales_rep_list = merged_df['Sales Rep'].unique().tolist()
sales_rep_list.insert(0, 'All')  # Add 'All' option

# Sales rep email mapping (for future use)
email_to_sales_rep = {
    'kaitlyn.surry@kcstorefixtures.com': 'Kaitlyn Surry',
    'roger.dixon@kcstorefixtures': 'Roger Dixon',
    'lorim@kc-store-fixtures.com': 'Kaitlyn Surry',
    'shelley.gummig@kcstorefixtures': 'Shelley Gummig',
    'ray.brown@kcstorefixtures': 'Ray Brown',
}

sales_rep_filter = st.sidebar.multiselect(
    'Sales Rep', 
    options=sales_rep_list,
    default=['All']
)

# Shipping Method Filter
ship_via_mapping = {
    'Small Package': [
        'Fed Ex 2Day', 'Fed Ex Ground', 'Fed Ex Express Saver', 
        'Fed Ex Ground Home Delivery', 'UPS Ground', 'DHL', 
        'FedEx Standard Overnight', 'FedEx Prior Overnight Saturday', 
        'FedEx International Ground', 'Fed Ex Priority Overnight', 
        'FedEx First Overnight® Saturday', 'Fed Ex International Priority'
    ],
    'LTL': [
        'Dayton Freight', 'Forward Air', 'Cross Country Freight', 
        'EPES - Truckload', 'Estes Standard', 'SAIA', '*LTL Best Way', 
        'FedEx Freight® Economy', 'Magnum Freight', 'Old Dominion', 
        'R&L Carriers', 'YRC Freight', 'XPO Logistics'
    ],
    'Truckload': ['24/7 - Truckload', 'EPES - Truckload'],
    'Our Truck': ['Our Truck', 'Our Truck - Small', 'Our Truck - Large'],
    'Pick Ups': ['Customer Pickup', 'In-Store Pickup'],
    'All': merged_df['Ship Via'].unique().tolist()
}

ship_via_filter = st.sidebar.multiselect(
    'Ship Via', 
    options=list(ship_via_mapping.keys()),
    default=['All']
)

# Ship Date Filter
date_filter_options = ['All Time', 'Today', 'Past (including today)', 'Future', 'Custom Range']
ship_date_filter = st.sidebar.selectbox('Ship Date', options=date_filter_options)

# Custom date range inputs
if ship_date_filter == 'Custom Range':
    start_date = st.sidebar.date_input('Start Date', datetime.today() - timedelta(days=7))
    end_date = st.sidebar.date_input('End Date', datetime.today())
else:
    start_date = None
    end_date = None

# Task Status Filters
tasked_orders = st.sidebar.checkbox('Tasked Orders', value=True)
untasked_orders = st.sidebar.checkbox('Untasked Orders', value=True)

# =============================================================================
# DATA FILTERING
# =============================================================================

# Apply Sales Rep filter
if 'All' not in sales_rep_filter:
    merged_df = merged_df[merged_df['Sales Rep'].isin(sales_rep_filter)]

# Apply Ship Via filter
if 'All' not in ship_via_filter:
    filtered_ship_vias = [ship_via for key in ship_via_filter for ship_via in ship_via_mapping[key]]
    merged_df = merged_df[merged_df['Ship Via'].isin(filtered_ship_vias)]

# Apply Ship Date filter
today = pd.to_datetime(datetime.today())
if ship_date_filter == 'Today':
    merged_df = merged_df[merged_df['Ship Date'].dt.date == today.date()]
elif ship_date_filter == 'Past (including today)':
    merged_df = merged_df[merged_df['Ship Date'] <= today]
elif ship_date_filter == 'Future':
    merged_df = merged_df[merged_df['Ship Date'] > today]
elif ship_date_filter == 'Custom Range' and start_date and end_date:
    merged_df = merged_df[
        (merged_df['Ship Date'] >= pd.to_datetime(start_date)) & 
        (merged_df['Ship Date'] <= pd.to_datetime(end_date))
    ]

# Apply Task Status filter
if tasked_orders and not untasked_orders:
    merged_df = merged_df[merged_df['Task ID'].notna()]
elif untasked_orders and not tasked_orders:
    merged_df = merged_df[merged_df['Task ID'].isna()]

# Remove duplicate orders
merged_df = merged_df.drop_duplicates(subset=['Order Number'])

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

# Create tabs for different views
tab1, tab2 = st.tabs(["Open Orders", "Shipping Calendar"])

# Tab 1: Open Orders Dashboard
with tab1:
    # Calculate key metrics
    total_orders = len(merged_df)
    tasked_orders_count = merged_df['Task ID'].notna().sum()
    untasked_orders_count = merged_df['Task ID'].isna().sum()
    task_percentage = (tasked_orders_count / total_orders) * 100 if total_orders > 0 else 0

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Open Orders", total_orders)
    col2.metric("Tasked Orders", tasked_orders_count)
    col3.metric("Untasked Orders", untasked_orders_count)
    col4.metric("Task Completion Rate", f"{task_percentage:.1f}%")

    # Visualizations
    if not merged_df.empty:
        col_chart, col_pie = st.columns([2, 1])

        # Line chart: Orders by ship date
        with col_chart:
            ship_date_counts = merged_df['Ship Date'].value_counts().sort_index()
            if not ship_date_counts.empty:
                ship_date_counts_df = pd.DataFrame(ship_date_counts).reset_index()
                ship_date_counts_df.columns = ['Ship Date', 'Number of Orders']
                ship_date_counts_df['Ship Date'] = pd.to_datetime(ship_date_counts_df['Ship Date'], errors='coerce')

                fig_line = px.line(
                    ship_date_counts_df, 
                    x='Ship Date', 
                    y='Number of Orders', 
                    title='Open Orders by Ship Date',
                    labels={'Ship Date': 'Ship Date', 'Number of Orders': 'Number of Orders'}
                )
                st.plotly_chart(fig_line, use_container_width=True)

        # Pie chart: Tasked vs Untasked orders
        with col_pie:
            pie_data = pd.DataFrame({
                'Task Status': ['Tasked Orders', 'Untasked Orders'], 
                'Count': [tasked_orders_count, untasked_orders_count]
            })
            fig_pie = px.pie(
                pie_data, 
                names='Task Status', 
                values='Count', 
                title='Task Status Distribution',
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

    # Detailed data table
    with st.expander("View Filtered Orders", expanded=True):
        st.dataframe(merged_df, use_container_width=True)

# Tab 2: Shipping Calendar
with tab2:
    st.header("Weekly Shipping Calendar")
    
    # Prepare calendar data
    merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'])
    merged_df['Week'] = merged_df['Ship Date'].dt.isocalendar().week
    merged_df['Day'] = merged_df['Ship Date'].dt.day_name()
    merged_df['Week Start'] = merged_df['Ship Date'] - pd.to_timedelta(merged_df['Ship Date'].dt.weekday, unit='D')
    merged_df['Week End'] = merged_df['Week Start'] + timedelta(days=6)

    # Get unique weeks
    unique_weeks = merged_df[['Week', 'Week Start', 'Week End']].drop_duplicates().sort_values(by='Week')

    # Display day headers
    col_mon, col_tue, col_wed, col_thu, col_fri = st.columns(5)
    for col, day in zip([col_mon, col_tue, col_wed, col_thu, col_fri], 
                       ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']):
        with col:
            st.write(f"**{day}**")

    # Display weekly calendar
    for _, week_row in unique_weeks.iterrows():
        week_start = week_row['Week Start']
        week_days = [week_start + timedelta(days=i) for i in range(5)]

        for col, day, specific_date in zip([col_mon, col_tue, col_wed, col_thu, col_fri], 
                                         ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 
                                         week_days):
            day_orders = merged_df[
                (merged_df['Week Start'] == week_start) & 
                (merged_df['Day'] == day)
            ]

            formatted_date = specific_date.strftime('%B %d') if pd.notna(specific_date) else "Invalid Date"

            with col:
                if len(day_orders) > 0:
                    with st.expander(f"{formatted_date} ({len(day_orders)} Orders)"):
                        st.dataframe(day_orders, use_container_width=True)
                else:
                    with st.expander(f"{formatted_date}: No Orders"):
                        st.info("No orders scheduled for this day.")

        st.write("")  # Visual separation between weeks

    # Our Truck Orders Section
    st.header("Our Truck Orders - To Be Scheduled")
    st.info("This section shows orders assigned to our truck delivery that need scheduling.")
    
    truck_order_count = len(our_truck_data)
    with st.expander(f"Our Truck Orders ({truck_order_count} orders)"):
        st.dataframe(our_truck_data, use_container_width=True)
        st.markdown(
            "[View in NetSuite](https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5147&whence=)", 
            unsafe_allow_html=True
        )
