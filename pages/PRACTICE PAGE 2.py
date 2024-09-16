import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
import pandas as pd
import plotly.express as px
from utils.data_functions import process_netsuite_data_csv
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping
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

page_name = 'Practice Page'  # Updated page name as per your request
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

def apply_mapping(column, mapping_dict):
    return column.map(mapping_dict).fillna(column)

def format_currency(value):
    return "${:,.2f}".format(value) if pd.notna(value) else value

@st.cache_data(ttl=600)  # Cache data for 10 minutes
def load_data(url_open_so):
    logger.info("Attempting to fetch data from NetSuite restlet")
    df = process_netsuite_data_csv(url_open_so)
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
    
    # Convert 'Ship Date' to datetime, coerce invalid values
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
    
    # Drop rows where 'Ship Date' is NaT (invalid date)
    df = df.dropna(subset=['Ship Date'])

    # Check for and handle invalid 'Amount Remaining' values
    df['Amount Remaining'] = pd.to_numeric(df['Amount Remaining'], errors='coerce')
    
    return df

def filter_data(df, selected_sales_reps, selected_ship_vias):
    # Filter by Sales Rep
    if selected_sales_reps:
        df = df[df['Sales Rep'].isin(selected_sales_reps)]
    # Filter by Ship Via
    if selected_ship_vias:
        df = df[df['Ship Via'].isin(selected_ship_vias)]

    return df  # No date filtering

def display_filters(df):
    st.sidebar.header("Filters")
    # Sales Rep Filter
    sales_reps = sorted(df['Sales Rep'].dropna().unique())
    selected_sales_reps = st.sidebar.multiselect("Sales Reps", sales_reps, default=sales_reps)
    
    # Ship Via Filter
    ship_vias = sorted(df['Ship Via'].dropna().unique())
    selected_ship_vias = st.sidebar.multiselect("Ship Via", ship_vias, default=ship_vias)
    
    # Return filters without the date filter
    return selected_sales_reps, selected_ship_vias

def display_charts(df):
    if df.empty:
        st.warning("No data available for the selected filters.")
        return
    # Open Sales Orders by Ship Date
    ship_date_counts = df['Ship Date'].dt.date.value_counts().sort_index()
    fig_line = px.line(
        x=ship_date_counts.index,
        y=ship_date_counts.values,
        labels={'x': 'Ship Date', 'y': 'Number of Orders'},
        title='Open Sales Orders by Ship Date'
    )
    st.plotly_chart(fig_line, use_container_width=True)
    # Orders by Ship Via
    ship_via_counts = df['Ship Via'].value_counts()
    fig_pie = px.pie(
        values=ship_via_counts.values,
        names=ship_via_counts.index,
        title='Orders by Ship Via'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

def display_metrics(df):
    total_orders = len(df)
    if 'Amount Remaining' in df.columns:
        # Ensure 'Amount Remaining' is numeric
        total_amount_remaining = df['Amount Remaining'].sum()
    else:
        total_amount_remaining = 0
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Open Orders", total_orders)
    with col2:
        st.metric("Total Amount Remaining", format_currency(total_amount_remaining))

def display_data_table(df):
    with st.expander("View Data Table"):
        st.write(f"Total records after filtering: {len(df)}")
        st.dataframe(df)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="filtered_sales_orders.csv",
            mime="text/csv"
        )

def main():
    st.title("Open Sales Orders Analysis")
    st.success("You have access to this page.")
    try:
        # Load Data
        df = load_data(st.secrets["url_open_so"])
        if df is None or df.empty:
            return
        # Preprocess Data
        df = preprocess_data(df)
        # Display Filters and get user selection
        selected_sales_reps, selected_ship_vias = display_filters(df)
        # Apply Filters
        df_filtered = filter_data(df, selected_sales_reps, selected_ship_vias)
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
