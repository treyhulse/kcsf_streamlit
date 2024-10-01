import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(page_title="Shipping Report", 
                   page_icon="🚚",
                   layout="wide",)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Shipping Report")

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

import streamlit as st
from utils.restlet import fetch_restlet_data
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Cache the raw data fetching process, reset cache every 2 minutes (120 seconds)
@st.cache_data(ttl=120)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Fetch raw data
open_order_data = fetch_raw_data("customsearch5065")
pick_task_data = fetch_raw_data("customsearch5066")
our_truck_data = fetch_raw_data("customsearch5147")

# Select only 'Order Number' and 'Task ID' from pick_task_data
pick_task_data = pick_task_data[['Order Number', 'Task ID']]

# Merge the two dataframes on 'Order Number', keeping all rows from open_order_data
merged_df = pd.merge(open_order_data, pick_task_data, on='Order Number', how='left')

# Convert 'Ship Date' to datetime format
merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'], errors='coerce')

# Sidebar filters (global for both tabs)
st.sidebar.header('Filters')

# Sales Rep filter with 'All' option
sales_rep_list = merged_df['Sales Rep'].unique().tolist()
sales_rep_list.insert(0, 'All')  # Add 'All' option to the beginning of the list

sales_rep_filter = st.sidebar.multiselect(
    'Sales Rep', 
    options=sales_rep_list, 
    default='All'
)

# Ship Via filter with 'All' option
ship_via_list = merged_df['Ship Via'].unique().tolist()
ship_via_list.insert(0, 'All')  # Add 'All' option to the beginning of the list

# **Pre-populate the Ship Via filter if the 'Our Truck' button is clicked**
if st.sidebar.button('Our Truck'):
    default_ship_via = ['Our Truck', 'Our Truck - Small', 'Our Truck - Large']
else:
    default_ship_via = 'All'

# Allow user to manually select Ship Via options but pre-populate if the button was clicked
ship_via_filter = st.sidebar.multiselect(
    'Ship Via', 
    options=ship_via_list, 
    default=default_ship_via
)
    
# Ship Date filter with 'All Time' option
date_filter_options = ['All Time', 'Today', 'Past (including today)', 'Future', 'Custom Range']
ship_date_filter = st.sidebar.selectbox(
    'Ship Date',
    options=date_filter_options
)

if ship_date_filter == 'Custom Range':
    start_date = st.sidebar.date_input('Start Date', datetime.today() - timedelta(days=7))
    end_date = st.sidebar.date_input('End Date', datetime.today())
else:
    start_date = None
    end_date = None

# Tasked Orders checkbox
tasked_orders = st.sidebar.checkbox('Tasked Orders', value=True)

# Untasked Orders checkbox
untasked_orders = st.sidebar.checkbox('Untasked Orders', value=True)

# Apply Ship Date filter
today = pd.to_datetime(datetime.today())  # Ensure 'today' is in datetime format

if ship_date_filter == 'Today':
    merged_df = merged_df[merged_df['Ship Date'].dt.date == today.date()]  # Compare dates only
elif ship_date_filter == 'Past (including today)':
    merged_df = merged_df[merged_df['Ship Date'] <= today]
elif ship_date_filter == 'Future':
    merged_df = merged_df[merged_df['Ship Date'] > today]
elif ship_date_filter == 'Custom Range' and start_date and end_date:
    merged_df = merged_df[(merged_df['Ship Date'] >= pd.to_datetime(start_date)) & 
                          (merged_df['Ship Date'] <= pd.to_datetime(end_date))]
# No filtering for 'All Time'

# Apply Sales Rep filter
if 'All' not in sales_rep_filter:
    merged_df = merged_df[merged_df['Sales Rep'].isin(sales_rep_filter)]

# Apply Ship Via filter
if 'All' not in ship_via_filter:
    merged_df = merged_df[merged_df['Ship Via'].isin(ship_via_filter)]

# Apply Tasked/Untasked Orders filter
if tasked_orders and not untasked_orders:
    merged_df = merged_df[merged_df['Task ID'].notna()]
elif untasked_orders and not tasked_orders:
    merged_df = merged_df[merged_df['Task ID'].isna()]

# Remove duplicate Order Numbers
merged_df = merged_df.drop_duplicates(subset=['Order Number'])

# Create tabs for Open Orders and Shipping Calendar
tab1, tab2 = st.tabs(["Open Orders", "Shipping Calendar"])

# Tab 1: Open Orders
with tab1:
    # Metrics
    total_orders = len(merged_df)
    tasked_orders_count = merged_df['Task ID'].notna().sum()
    untasked_orders_count = merged_df['Task ID'].isna().sum()
    task_percentage = (tasked_orders_count / total_orders) * 100 if total_orders > 0 else 0

    # Styling for the metrics boxes
    st.markdown("""
    <style>
    .metrics-box {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-title {
        margin: 0;
        font-size: 20px;
    }
    .metric-value {
        margin: 0;
        font-size: 28px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Display dynamic metric boxes
    metrics = [
        {"label": "Total Open Orders", "value": total_orders},
        {"label": "Tasked Orders", "value": tasked_orders_count},
        {"label": "Untasked Orders", "value": untasked_orders_count},
        {"label": "Successful Task Percentage", "value": f"{task_percentage:.2f}%"},
    ]

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    for col, metric in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metrics-box">
                <h3 class="metric-title">{metric['label']}</h3>
                <p class="metric-value">{metric['value']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Add visual separation
    st.write("")

    # Display charts using Plotly
    if not merged_df.empty:
        col_chart, col_pie = st.columns([2, 1])
        with col_chart:
            merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'])
            ship_date_counts = merged_df['Ship Date'].value_counts().sort_index()
            fig_line = px.line(x=ship_date_counts.index, y=ship_date_counts.values, labels={'x': 'Ship Date', 'y': 'Number of Orders'}, title='Open Sales Orders by Ship Date')
            st.plotly_chart(fig_line, use_container_width=True)
        
        with col_pie:
            matched_orders = merged_df['Task ID'].notna().sum()
            unmatched_orders = merged_df['Task ID'].isna().sum()
            pie_data = pd.DataFrame({'Task Status': ['Tasked Orders', 'Untasked Orders'], 'Count': [matched_orders, unmatched_orders]})
            fig_pie = px.pie(pie_data, names='Task Status', values='Count', title='Tasked vs Untasked Orders', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.write("No data available for the selected filters.")

    # Display filtered DataFrame in an expander
    with st.expander("View Open Orders with a Ship Date"):
        st.write(merged_df)

# Tab 2: Shipping Calendar
with tab2:
    st.header("Shipping Calendar")

    # Group orders by week and day
    merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'])
    merged_df['Week'] = merged_df['Ship Date'].dt.isocalendar().week
    merged_df['Day'] = merged_df['Ship Date'].dt.day_name()
    merged_df['Week Start'] = merged_df['Ship Date'] - pd.to_timedelta(merged_df['Ship Date'].dt.weekday, unit='D')
    merged_df['Week End'] = merged_df['Week Start'] + timedelta(days=6)

    # Get the unique weeks from the dataset
    unique_weeks = merged_df[['Week', 'Week Start', 'Week End']].drop_duplicates().sort_values(by='Week')

    # Display headers for the days of the week once at the top
    col_mon, col_tue, col_wed, col_thu, col_fri = st.columns(5)
    with col_mon:
        st.write("**Monday**")
    with col_tue:
        st.write("**Tuesday**")
    with col_wed:
        st.write("**Wednesday**")
    with col_thu:
        st.write("**Thursday**")
    with col_fri:
        st.write("**Friday**")

    # Iterate through the unique weeks
    for _, week_row in unique_weeks.iterrows():
        week_start = week_row['Week Start']
        week_days = [week_start + timedelta(days=i) for i in range(5)]  # Monday to Friday

        # Populate columns with orders for each day, including the specific date
        for col, day, specific_date in zip([col_mon, col_tue, col_wed, col_thu, col_fri], 
                                           ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 
                                           week_days):
            day_orders = merged_df[(merged_df['Week Start'] == week_start) & (merged_df['Day'] == day)]

            # Check if specific_date is valid before formatting
            if pd.notna(specific_date):
                formatted_date = specific_date.strftime('%B %d')
            else:
                formatted_date = "Invalid Date"

            with col:
                if len(day_orders) > 0:
                    with st.expander(f"{formatted_date} ({len(day_orders)} Orders)"):
                        st.write(day_orders)
                else:
                    with st.expander(f"{formatted_date}: NO ORDERS"):
                        st.write("No orders for this day.")

        # Add visual separation between weeks
        st.write("")

    # Expander for customsearch5147 data with record count in header
    st.header("Our Truck Orders to be scheduled")
    st.subheader("This table will not be affected by filters. It only shows our truck orders with no ship date.")
    truck_order_count = len(our_truck_data)
    with st.expander(f"{truck_order_count} Orders"):
        st.write(our_truck_data)
        st.markdown("[View in NetSuite](https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5147&whence=)", unsafe_allow_html=True)
