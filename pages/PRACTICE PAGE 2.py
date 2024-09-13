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

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"You have access to this page.")

def apply_mapping(column, mapping_dict):
    return column.apply(lambda x: mapping_dict.get(x, x))

def format_currency(value):
    return "${:,.2f}".format(value) if pd.notna(value) else value

def get_date_range(preset):
    today = date.today()
    if preset == "Today":
        return today, today
    elif preset == "This Week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        return start_of_week, end_of_week
    elif preset == "This Month":
        start_of_month = today.replace(day=1)
        end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return start_of_month, end_of_month
    else:
        return None, None

def main():
    st.header("Open Sales Orders Analysis")
    
    try:
        # Fetch Data
        with st.spinner("Fetching Open Sales Orders..."):
            logger.info("Attempting to fetch data from NetSuite restlet")
            df_open_so = process_netsuite_data_csv(st.secrets["url_open_so"])
        
        if df_open_so is None or df_open_so.empty:
            st.warning("No data retrieved from the restlet. The dataframe is empty or None.")
            logger.warning("Retrieved dataframe is empty or None")
            return

        logger.info(f"Successfully retrieved data. Shape: {df_open_so.shape}")
        st.success(f"Data loaded successfully! Number of records: {len(df_open_so)}")

        # Display raw data for debugging
        with st.expander("Debug: View Raw Data"):
            st.write("First few rows of raw data:")
            st.write(df_open_so.head())
            st.write("Data types:")
            st.write(df_open_so.dtypes)
            st.write("Column names:")
            st.write(df_open_so.columns.tolist())

        # Apply mapping
        logger.info("Applying mappings to columns")
        df_open_so['Ship Via'] = apply_mapping(df_open_so['Ship Via'], ship_via_mapping)
        df_open_so['Terms'] = apply_mapping(df_open_so['Terms'], terms_mapping)
        df_open_so['Sales Rep'] = apply_mapping(df_open_so['Sales Rep'], sales_rep_mapping)

        # Display filters
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Filter by Sales Rep")
            sales_reps = ['All'] + sorted(df_open_so['Sales Rep'].unique())
            selected_sales_reps = st.multiselect("Select Sales Reps", sales_reps, default=['All'])

        with col2:
            st.subheader("Filter by Ship Via")
            ship_vias = ['All'] + sorted(df_open_so['Ship Via'].unique())
            selected_ship_vias = st.multiselect("Select Ship Via", ship_vias, default=['All'])

        with col3:
            st.subheader("Filter by Ship Date")
            date_preset = st.selectbox("Select date range preset", ["Custom", "Today", "This Week", "This Month"])
            
            if date_preset == "Custom":
                min_date = pd.to_datetime(df_open_so['Ship Date']).min().date()
                max_date = pd.to_datetime(df_open_so['Ship Date']).max().date()
                selected_date_range = st.date_input("Select custom date range", [min_date, max_date], min_value=min_date, max_value=max_date)
            else:
                start_date, end_date = get_date_range(date_preset)
                st.write(f"Selected range: {start_date} to {end_date}")
                selected_date_range = [start_date, end_date]

        # Apply filters
        logger.info("Applying filters to data")
        if 'All' not in selected_sales_reps:
            df_open_so = df_open_so[df_open_so['Sales Rep'].isin(selected_sales_reps)]
        if 'All' not in selected_ship_vias:
            df_open_so = df_open_so[df_open_so['Ship Via'].isin(selected_ship_vias)]

        # Apply Ship Date filter
        df_open_so['Ship Date'] = pd.to_datetime(df_open_so['Ship Date'])
        df_open_so = df_open_so[(df_open_so['Ship Date'].dt.date >= selected_date_range[0]) & (df_open_so['Ship Date'].dt.date <= selected_date_range[1])]

        # Display charts
        if not df_open_so.empty:
            logger.info("Creating and displaying charts")
            col_chart, col_pie = st.columns([2, 1])
            with col_chart:
                ship_date_counts = df_open_so['Ship Date'].dt.date.value_counts().sort_index()
                fig = px.line(x=ship_date_counts.index, y=ship_date_counts.values, labels={'x': 'Ship Date', 'y': 'Number of Orders'}, title='Open Sales Orders by Ship Date')
                st.plotly_chart(fig, use_container_width=True)
            with col_pie:
                ship_via_counts = df_open_so['Ship Via'].value_counts()
                fig = px.pie(values=ship_via_counts.values, names=ship_via_counts.index, title='Orders by Ship Via')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the selected filters.")
            logger.warning("No data available after applying filters")

        # Display metrics
        total_orders = len(df_open_so)
        total_amount = df_open_so['Amount'].sum() if 'Amount' in df_open_so.columns else 0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Open Orders", total_orders)
        with col2:
            st.metric("Total Amount", f"${total_amount:,.2f}")

        # Data table and download option
        with st.expander("View Data Table"):
            st.write(f"Total records after filtering: {len(df_open_so)}")
            st.dataframe(df_open_so, height=400)
            csv = df_open_so.to_csv(index=False)
            st.download_button(label="Download filtered data as CSV", data=csv, file_name="filtered_sales_orders.csv", mime="text/csv")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Exception occurred: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("Please check the logs for more details.")

if __name__ == "__main__":
    main()