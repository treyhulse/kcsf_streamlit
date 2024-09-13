import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

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


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
from utils.data_functions import process_netsuite_data_csv
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping
from datetime import date, timedelta
import streamlit as st
import time

# Function to apply mapping, but keep unmapped IDs as raw values
def apply_mapping(column, mapping_dict):
    return column.apply(lambda x: mapping_dict.get(x, x))

# Function to format currency
def format_currency(value):
    return "${:,.2f}".format(value) if pd.notna(value) else value

# Function to filter by date range (including Next Month, Last Week, etc.)
def get_date_range(preset):
    today = date.today()
    if preset == "Today":
        return today, today
    elif preset == "This Week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        return start_of_week, end_of_week
    elif preset == "Last Week":
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=4)
        return start_of_last_week, end_of_last_week
    elif preset == "Next Week":
        start_of_next_week = today + timedelta(days=(7 - today.weekday()))
        end_of_next_week = start_of_next_week + timedelta(days=4)
        return start_of_next_week, end_of_next_week
    elif preset == "This Month":
        start_of_month = today.replace(day=1)
        end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return start_of_month, end_of_month
    elif preset == "Next Month":
        start_of_next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_of_next_month = (start_of_next_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return start_of_next_month, end_of_next_month
    else:
        return None, None

# Main function
def main():
    # Define tabs
    tab1, tab2 = st.tabs(["Open Sales Orders Analysis", "Shipping Calendar"])

    # Tab 1: Open Sales Orders Analysis
    with tab1:
        st.header("Open Sales Orders Analysis")
        
        # Fetch Data
        with st.spinner("Fetching Open Sales Orders..."):
            df_open_so = process_netsuite_data_csv(st.secrets["url_open_so"])
        with st.spinner("Fetching RF Pick Data..."):
            df_rf_pick = process_netsuite_data_csv(st.secrets["url_rf_pick"])

        # Apply mapping (with error handling)
        if 'Ship Via' in df_open_so.columns:
            df_open_so['Ship Via'] = df_open_so['Ship Via'].map(ship_via_mapping).fillna('Unknown')
        if 'Terms' in df_open_so.columns:
            df_open_so['Terms'] = df_open_so['Terms'].map(terms_mapping).fillna('Unknown')

        # Display filters in four columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.subheader("Filter by Sales Rep")
            if 'Sales Rep' in df_open_so.columns:
                sales_reps = ['All'] + sorted([sales_rep_mapping.get(rep_id, 'Unknown') for rep_id in df_open_so['Sales Rep'].unique()])
                selected_sales_reps = st.multiselect("Select Sales Reps", sales_reps, default=['All'])
            else:
                st.write("Sales Rep data not available")
                selected_sales_reps = ['All']

        with col2:
            st.subheader("Filter by Ship Via")
            if 'Ship Via' in df_open_so.columns:
                ship_vias = ['All'] + sorted(df_open_so['Ship Via'].unique())
                selected_ship_vias = st.multiselect("Select Ship Via", ship_vias, default=['All'])
            else:
                st.write("Ship Via data not available")
                selected_ship_vias = ['All']

        with col3:
            st.subheader("Filter by Ship Date")
            if 'Ship Date' in df_open_so.columns:
                date_preset = st.selectbox("Select date range preset", ["Custom", "Today", "Tomorrow", "This Week", "This Month"])
                
                if date_preset == "Custom":
                    min_date = pd.to_datetime(df_open_so['Ship Date']).min()
                    max_date = pd.to_datetime(df_open_so['Ship Date']).max()
                    selected_date_range = st.date_input("Select custom date range", [min_date, max_date], min_value=min_date, max_value=max_date)
                else:
                    start_date, end_date = get_date_range(date_preset)
                    st.write(f"Selected range: {start_date} to {end_date}")
                    selected_date_range = [start_date, end_date]
            else:
                st.write("Ship Date data not available")
                selected_date_range = [date.today(), date.today()]

        with col4:
            st.subheader("Filter by Task ID")
            filter_with_task_id = st.checkbox("Show rows with Task ID", value=True)
            filter_without_task_id = st.checkbox("Show rows without Task ID", value=True)

        # Normalize 'Ship Date' column to MM/DD/YYYY
        if 'Ship Date' in df_open_so.columns:
            df_open_so['Ship Date'] = pd.to_datetime(df_open_so['Ship Date']).dt.strftime('%m/%d/%Y')

        # Merge data
        if 'Order Number' in df_open_so.columns and 'Order Number' in df_rf_pick.columns:
            merged_df = pd.merge(df_open_so, df_rf_pick[['Task ID', 'Order Number']].drop_duplicates(), on='Order Number', how='left')
        else:
            st.error("Unable to merge data: 'Order Number' column missing in one or both DataFrames")
            return

        if 'Sales Rep' in merged_df.columns:
            merged_df['Sales Rep'] = merged_df['Sales Rep'].replace(sales_rep_mapping)
        if 'Order Number' in merged_df.columns:
            merged_df['Order Number'] = merged_df['Order Number'].astype(str)

        # Apply filters
        if 'All' not in selected_sales_reps and 'Sales Rep' in merged_df.columns:
            merged_df = merged_df[merged_df['Sales Rep'].isin(selected_sales_reps)]
        if 'All' not in selected_ship_vias and 'Ship Via' in merged_df.columns:
            merged_df = merged_df[merged_df['Ship Via'].isin(selected_ship_vias)]

        # Apply Ship Date filter
        if 'Ship Date' in merged_df.columns:
            merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'], format='%m/%d/%Y')
            merged_df = merged_df[(merged_df['Ship Date'] >= pd.to_datetime(selected_date_range[0])) & (merged_df['Ship Date'] <= pd.to_datetime(selected_date_range[1]))]

        # Apply Task ID filters
        if 'Task ID' in merged_df.columns:
            if filter_with_task_id and not filter_without_task_id:
                merged_df = merged_df[merged_df['Task ID'].notna()]
            elif filter_without_task_id and not filter_with_task_id:
                merged_df = merged_df[merged_df['Task ID'].isna()]

        # Display metrics
        total_orders = len(merged_df)
        matched_orders = merged_df['Task ID'].notna().sum() if 'Task ID' in merged_df.columns else 0
        unmatched_orders = merged_df['Task ID'].isna().sum() if 'Task ID' in merged_df.columns else 0
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
            st.write(f"Total records after filtering: {len(merged_df)}")
            st.dataframe(merged_df, height=400)
            csv = merged_df.to_csv(index=False)
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

        df = process_netsuite_data_csv(st.secrets["url_open_so"])

        # Normalize 'Ship Date' to MM/DD/YYYY format
        if 'Ship Date' in df.columns:
            df['Ship Date'] = pd.to_datetime(df['Ship Date']).dt.strftime('%m/%d/%Y')
        if 'Order Number' in df.columns:
            df['Order Number'] = df['Order Number'].astype(str)
        if 'Amount Remaining' in df.columns:
            df['Amount Remaining'] = df['Amount Remaining'].apply(format_currency)

        # Map relevant columns
        if 'Ship Via' in df.columns:
            df['Ship Via'] = apply_mapping(df['Ship Via'], ship_via_mapping)
        if 'Sales Rep' in df.columns:
            df['Sales Rep'] = apply_mapping(df['Sales Rep'], sales_rep_mapping)
        if 'Terms' in df.columns:
            df['Terms'] = apply_mapping(df['Terms'], terms_mapping)

        # Display Ship Via and Date Range filters in two columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Select Ship Via")
            if 'Ship Via' in df.columns:
                ship_vias = ['All'] + df['Ship Via'].unique().tolist()
                selected_ship_vias = st.multiselect("Ship Via", ship_vias, default=['All'])

                if 'All' in selected_ship_vias:
                    selected_ship_vias = df['Ship Via'].unique().tolist()
            else:
                st.write("Ship Via data not available")
                selected_ship_vias = ['All']

        with col2:
            st.subheader("Select Date Range")
            date_preset = st.selectbox("Select Date Range", ["This Week", "Next Week", "Last Week", "This Month", "Next Month"])
            start_date, end_date = get_date_range(date_preset)

        # Apply filters
        if 'Ship Via' in df.columns and 'Ship Date' in df.columns:
            df_filtered = df[
                (df['Ship Via'].isin(selected_ship_vias)) &
                (pd.to_datetime(df['Ship Date']) >= pd.to_datetime(start_date)) &
                (pd.to_datetime(df['Ship Date']) <= pd.to_datetime(end_date))
            ]
        else:
            st.error("Unable to filter data: 'Ship Via' or 'Ship Date' column missing")
            return

        # Display by weekday
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        days = pd.date_range(start=start_date, end=end_date, freq='B').strftime('%m/%d/%Y')

        for day_name in weekdays:
            st.subheader(day_name)
            for date_str in days:
                date_obj = pd.to_datetime(date_str)
                if date_obj.strftime('%A') == day_name:
                    orders_today = df_filtered[df_filtered['Ship Date'] == date_str]
                    if not orders_today.empty:
                        total_orders = len(orders_today)
                        with st.expander(f"{date_str} - Total Orders: {total_orders}"):
                            st.dataframe(orders_today)
                    else:
                        with st.expander(f"{date_str} - No shipments"):
                            st.write("No orders for this day.")

if __name__ == "__main__":
    main()