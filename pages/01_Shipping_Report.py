import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from typing import Tuple, Optional

from utils.data_functions import process_netsuite_data, replace_ids_with_display_values
from utils.config import API_URLS, SALES_REP_MAPPING, SHIP_VIA_MAPPING, TERMS_MAPPING
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set page config
st.set_page_config(page_title="Shipping Report", layout="wide")

@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    df = process_netsuite_data(API_URLS["open_so"])
    df = replace_ids_with_display_values(df, SALES_REP_MAPPING, 'Sales Rep')
    df = replace_ids_with_display_values(df, SHIP_VIA_MAPPING, 'Ship Via')
    df = replace_ids_with_display_values(df, TERMS_MAPPING, 'Terms')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    return df

def create_ship_date_chart(df: pd.DataFrame):
    ship_date_counts = df['Ship Date'].value_counts().sort_index()
    fig = px.line(
        x=ship_date_counts.index,
        y=ship_date_counts.values,
        labels={'x': 'Ship Date', 'y': 'Number of Orders'},
        title='Open Sales Orders by Ship Date'
    )
    fig.update_layout(
        xaxis_title='Ship Date',
        yaxis_title='Number of Orders',
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

def create_pie_chart(matched_orders: int, unmatched_orders: int):
    pie_data = pd.DataFrame({
        'Task Status': ['Tasked Orders', 'Untasked Orders'],
        'Count': [matched_orders, unmatched_orders]
    })
    fig = px.pie(
        pie_data,
        names='Task Status',
        values='Count',
        title='Tasked vs Untasked Orders',
        hole=0.4
    )
    fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))
    return fig

def get_date_range(preset: str) -> Tuple[Optional[date], Optional[date]]:
    today = date.today()
    if preset == "Today":
        return today, today
    elif preset == "Tomorrow":
        return today + timedelta(days=1), today + timedelta(days=1)
    elif preset == "This Week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week
    elif preset == "This Month":
        start_of_month = today.replace(day=1)
        next_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_of_month = next_month - timedelta(days=1)
        return start_of_month, end_of_month
    else:
        return None, None

def main():
    # Capture the user's email
    user_email = capture_user_email()
    if user_email is None:
        st.error("Unable to retrieve user information.")
        st.stop()

    # Validate access to this specific page
    page_name = 'Shipping Report'
    if not validate_page_access(user_email, page_name):
        show_permission_violation()
        st.stop()

    st.title("Shipping Report")

    # Load data
    with st.spinner("Loading data..."):
        df = load_data()

    # Sidebar filters
    st.sidebar.title("Filters")

    # Date filter
    st.sidebar.subheader("Filter by Ship Date")
    date_preset = st.sidebar.selectbox("Select date range preset", ["Custom", "Today", "Tomorrow", "This Week", "This Month"])

    if date_preset == "Custom":
        min_date = df['Ship Date'].min().date()
        max_date = df['Ship Date'].max().date()
        selected_date_range = st.sidebar.date_input("Select custom date range", [min_date, max_date], min_value=min_date, max_value=max_date)
    else:
        start_date, end_date = get_date_range(date_preset)
        st.sidebar.write(f"Selected range: {start_date} to {end_date}")
        selected_date_range = [start_date, end_date]

    # Sales Rep filter
    st.sidebar.subheader("Filter by Sales Rep")
    sales_reps = ['All'] + sorted(df['Sales Rep'].unique())
    selected_sales_reps = st.sidebar.multiselect("Select Sales Reps", sales_reps, default=['All'])

    # Ship Via filter
    st.sidebar.subheader("Filter by Ship Via")
    ship_vias = ['All'] + sorted(df['Ship Via'].unique())
    selected_ship_vias = st.sidebar.multiselect("Select Ship Via", ship_vias, default=['All'])

    # Task ID filters
    filter_with_task_id = st.sidebar.checkbox("Show rows with Task ID", value=True)
    filter_without_task_id = st.sidebar.checkbox("Show rows without Task ID", value=True)

    # Apply filters
    filtered_df = df.copy()

    # Date filter
    filtered_df = filtered_df[(filtered_df['Ship Date'].dt.date >= selected_date_range[0]) & 
                              (filtered_df['Ship Date'].dt.date <= selected_date_range[1])]

    # Sales Rep filter
    if 'All' not in selected_sales_reps:
        filtered_df = filtered_df[filtered_df['Sales Rep'].isin(selected_sales_reps)]

    # Ship Via filter
    if 'All' not in selected_ship_vias:
        filtered_df = filtered_df[filtered_df['Ship Via'].isin(selected_ship_vias)]

    # Task ID filter
    if filter_with_task_id and not filter_without_task_id:
        filtered_df = filtered_df[filtered_df['Task ID'].notna()]
    elif filter_without_task_id and not filter_with_task_id:
        filtered_df = filtered_df[filtered_df['Task ID'].isna()]

    # Display metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    total_orders = len(filtered_df)
    matched_orders = filtered_df['Task ID'].notna().sum()
    unmatched_orders = filtered_df['Task ID'].isna().sum()
    successful_task_percentage = (matched_orders / total_orders) * 100 if total_orders > 0 else 0

    col1.metric("Total Open Orders", total_orders)
    col2.metric("Tasked Orders", matched_orders)
    col3.metric("Untasked Orders", unmatched_orders)
    col4.metric("Successful Task Percentage", f"{successful_task_percentage:.2f}%")

    # Display charts
    st.subheader("Visualizations")
    col_chart, col_pie = st.columns([2, 1])

    with col_chart:
        st.plotly_chart(create_ship_date_chart(filtered_df), use_container_width=True)
    
    with col_pie:
        st.plotly_chart(create_pie_chart(matched_orders, unmatched_orders), use_container_width=True)

    # Display data table
    st.subheader("Filtered Data Table")
    st.write(f"Total records after filtering: {len(filtered_df)}")
    st.dataframe(filtered_df, height=400)

    # Download option
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_sales_orders.csv",
        mime="text/csv",
    )

    # Link to NetSuite
    st.markdown(
        """
        <br>
        <a href="https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5065&saverun=T&whence=" target="_blank">Link to open order report in NetSuite</a>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()