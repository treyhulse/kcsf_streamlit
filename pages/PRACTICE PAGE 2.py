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
    st.header("Open Sales Orders Data")

    # Fetch Data
    with st.spinner("Fetching Open Sales Orders..."):
        df_open_so = process_netsuite_data_csv(st.secrets["url_open_so"])
    with st.spinner("Fetching RF Pick Data..."):
        df_rf_pick = process_netsuite_data_csv(st.secrets["url_rf_pick"])

    # Apply mapping
    df_open_so['Ship Via'] = df_open_so['Ship Via'].map(ship_via_mapping).fillna('Unknown')
    df_open_so['Terms'] = df_open_so['Terms'].map(terms_mapping).fillna('Unknown')

    # Display filters in four columns (added Task ID as the fourth column)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("Filter by Sales Rep")
        sales_reps = ['All'] + sorted([sales_rep_mapping.get(rep_id, 'Unknown') for rep_id in df_open_so['Sales Rep'].unique()])
        selected_sales_reps = st.multiselect("Select Sales Reps", sales_reps, default=['All'])

    with col2:
        st.subheader("Filter by Ship Via")
        ship_vias = ['All'] + sorted(df_open_so['Ship Via'].unique())
        selected_ship_vias = st.multiselect("Select Ship Via", ship_vias, default=['All'])

    with col3:
        st.subheader("Filter by Ship Date")
        date_preset = st.selectbox("Select date range preset", ["Custom", "Today", "This Week", "This Month"])

        if date_preset == "Custom":
            min_date = pd.to_datetime(df_open_so['Ship Date']).min()
            max_date = pd.to_datetime(df_open_so['Ship Date']).max()
            selected_date_range = st.date_input("Select custom date range", [min_date, max_date], min_value=min_date, max_value=max_date)
        else:
            start_date, end_date = get_date_range(date_preset)
            st.write(f"Selected range: {start_date} to {end_date}")
            selected_date_range = [start_date, end_date]

    with col4:
        st.subheader("Filter by Task ID")
        filter_with_task_id = st.checkbox("Show rows with Task ID", value=True)
        filter_without_task_id = st.checkbox("Show rows without Task ID", value=True)

    # Normalize 'Ship Date' column to MM/DD/YYYY
    df_open_so['Ship Date'] = pd.to_datetime(df_open_so['Ship Date']).dt.strftime('%m/%d/%Y')

    # Merge data
    merged_df = pd.merge(df_open_so, df_rf_pick[['Task ID', 'Order Number']].drop_duplicates(), on='Order Number', how='left')
    merged_df['Sales Rep'] = merged_df['Sales Rep'].replace(sales_rep_mapping)
    merged_df['Order Number'] = merged_df['Order Number'].astype(str)

    # Apply filters
    if 'All' not in selected_sales_reps:
        merged_df = merged_df[merged_df['Sales Rep'].isin(selected_sales_reps)]
    if 'All' not in selected_ship_vias:
        merged_df = merged_df[merged_df['Ship Via'].isin(selected_ship_vias)]

    # Apply Ship Date filter
    merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'], format='%m/%d/%Y')
    merged_df = merged_df[(merged_df['Ship Date'] >= pd.to_datetime(selected_date_range[0])) & (merged_df['Ship Date'] <= pd.to_datetime(selected_date_range[1]))]

    # Apply Task ID filters
    if filter_with_task_id and not filter_without_task_id:
        merged_df = merged_df[merged_df['Task ID'].notna()]
    elif filter_without_task_id and not filter_with_task_id:
        merged_df = merged_df[merged_df['Task ID'].isna()]

    # Display DataFrame and download option
    if not merged_df.empty:
        st.write(f"Total records after filtering: {len(merged_df)}")
        st.dataframe(merged_df, height=400)
        csv = merged_df.to_csv(index=False)
        st.download_button(label="Download filtered data as CSV", data=csv, file_name="filtered_sales_orders.csv", mime="text/csv")
    else:
        st.write("No data available for the selected filters.")

if __name__ == "__main__":
    main()
