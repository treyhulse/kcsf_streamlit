import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
import pandas as pd
import plotly.express as px
from utils.data_functions import process_netsuite_data_csv
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping
from datetime import date, timedelta
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")

# User Authentication
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

page_name = 'Order Management Dashboard'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

def apply_mapping(column, mapping_dict):
    return column.map(mapping_dict).fillna(column)

def format_currency(value):
    return "${:,.2f}".format(value) if pd.notna(value) else value

def get_date_range(preset):
    today = date.today()
    if preset == "Today":
        return today, today
    elif preset == "This Week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week
    elif preset == "This Month":
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return start_of_month, end_of_month
    else:
        return None, None

@st.cache_data(ttl=600)  # Cache data for 10 minutes
def load_data(url):
    logger.info("Attempting to fetch data from NetSuite restlet")
    df = process_netsuite_data_csv(url)
    if df is None or df.empty:
        logger.warning("Retrieved dataframe is empty or None")
        st.warning("No data retrieved from the data source.")
    else:
        logger.info(f"Successfully retrieved data. Shape: {df.shape}")
    return df

def preprocess_data(df):
    # Apply mappings
    df['Ship Via'] = apply_mapping(df['Ship Via'], ship_via_mapping)
    df['Terms'] = apply_mapping(df['Terms'], terms_mapping)
    df['Sales Rep'] = apply_mapping(df['Sales Rep'], sales_rep_mapping)
    # Convert 'Ship Date' to datetime
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    return df

def filter_data(df, selected_sales_reps, selected_ship_vias, date_range):
    # Filter by Sales Rep
    if selected_sales_reps:
        df = df[df['Sales Rep'].isin(selected_sales_reps)]
    # Filter by Ship Via
    if selected_ship_vias:
        df = df[df['Ship Via'].isin(selected_ship_vias)]
    # Filter by Ship Date
    if date_range:
        start_date, end_date = date_range
        df = df[(df['Ship Date'].dt.date >= start_date) & (df['Ship Date'].dt.date <= end_date)]
    return df

def display_filters(df):
    st.sidebar.header("Filters")
    # Sales Rep Filter
    sales_reps = sorted(df['Sales Rep'].dropna().unique())
    selected_sales_reps = st.sidebar.multiselect("Sales Reps", sales_reps, default=sales_reps)
    # Ship Via Filter
    ship_vias = sorted(df['Ship Via'].dropna().unique())
    selected_ship_vias = st.sidebar.multiselect("Ship Via", ship_vias, default=ship_vias)
    # Ship Date Filter
    date_preset = st.sidebar.selectbox("Date Range Preset", ["Custom", "Today", "This Week", "This Month"], index=3)
    if date_preset == "Custom":
        min_date = df['Ship Date'].min().date()
        max_date = df['Ship Date'].max().date()
        start_date, end_date = st.sidebar.date_input("Ship Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    else:
        start_date, end_date = get_date_range(date_preset)
    return selected_sales_reps, selected_ship_vias, (start_date, end_date)

def display_charts(df):
    if df.empty:
        st.warning("No data available for the selected filters.")
        return
    # Open Sales Orders by Ship Date
    ship_date_counts = df['Ship Date'].dt.date.value_counts().sort_index()
    fig_line = px.line(x=ship_date_counts.index, y=ship_date_counts.values, labels={'x': 'Ship Date', 'y': 'Number of Orders'}, title='Open Sales Orders by Ship Date')
    st.plotly_chart(fig_line, use_container_width=True)
    # Orders by Ship Via
    ship_via_counts = df['Ship Via'].value_counts()
    fig_pie = px.pie(values=ship_via_counts.values, names=ship_via_counts.index, title='Orders by Ship Via')
    st.plotly_chart(fig_pie, use_container_width=True)

def display_metrics(df):
    total_orders = len(df)
    total_amount = df['Amount'].sum() if 'Amount' in df.columns else 0
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Open Orders", total_orders)
    with col2:
        st.metric("Total Amount", format_currency(total_amount))

def display_data_table(df):
    with st.expander("View Data Table"):
        st.write(f"Total records after filtering: {len(df)}")
        st.dataframe(df)
        csv = df.to_csv(index=False)
        st.download_button(label="Download data as CSV", data=csv, file_name="filtered_sales_orders.csv", mime="text/csv")

def main():
    st.title("Order Management Dashboard")
    st.success("You have access to this page.")
    try:
        # Load Data
        df = load_data(st.secrets["url_open_so"])
        if df is None or df.empty:
            return
        # Preprocess Data
        df = preprocess_data(df)
        # Display Filters and get user selection
        selected_sales_reps, selected_ship_vias, date_range = display_filters(df)
        # Apply Filters
        df_filtered = filter_data(df, selected_sales_reps, selected_ship_vias, date_range)
        # Display Metrics
        display_metrics(df_filtered)
        # Display Charts
        display_charts(df_filtered)
        # Display Data Table
        display_data_table(df_filtered)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Exception occurred: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("Please check the logs for more details.")

if __name__ == "__main__":
    main()
