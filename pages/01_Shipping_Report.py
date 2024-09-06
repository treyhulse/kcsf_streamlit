import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

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
from utils.data_functions import process_netsuite_data_csv
from datetime import date, timedelta


# Sales Rep mapping
sales_rep_mapping = {
    7: "Shelley Gummig",
    61802: "Kaitlyn Surry",
    4125270: "Becky Dean",
    4125868: "Roger Dixon",
    4131659: "Lori McKiney",
    47556: "Raymond Brown",
    4169685: "Shellie Pritchett",
    4123869: "Katelyn Kennedy",
    47708: "Phil Vaughan",
    4169200: "Dave Knudtson",
    4168032: "Trey Hulse",
    4152972: "Gary Bargen",
    4159935: "Derrick Lewis",
    66736: "Unspecified",
    67473: 'Jon Joslin',
}

# Ship Via mapping
ship_via_mapping = {
    141: "Our Truck",
    32356: "EPES - Truckload",
    226: "Pickup 2",
    36191: "Estes Standard",
    36: "Fed Ex Ground",
    3653: "Fed Ex Ground Home Delivery",
    7038: "Other - See Shipping Info",
    4: "UPS Ground",
    227: "Dayton Freight"
}

# Terms mapping
terms_mapping = {
    2: "Net 30",
    11: "Credit Card - Prepay",
    10: "Prepay",
    13: "Net 45",
    3: "Net 60",
    19: "Check",
    27: "ACH",
    37: "Account Credit",
    18: "No Charge"
}

st.markdown(
    """
    <style>
    .metric-box {
        background-color: var(--primary-background-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def create_ship_date_chart(df):
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
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

def create_pie_chart(matched_orders, unmatched_orders):
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

def get_date_range(preset):
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
    with st.spinner("Fetching Open Sales Orders..."):
        df_open_so = process_netsuite_data_csv(st.secrets["url_open_so"])

    # Display the DataFrame before any processing
    st.write(df_open_so.head())  # This will show the first few rows of the DataFrame
    
    # Check if 'Ship Via' exists
    if 'Ship Via' in df_open_so.columns:
        st.write("Ship Via column found")  # This will confirm if the column is present
    else:
        st.warning("The 'Ship Via' column is missing from the data.")
    
    # Continue with the rest of your logic
    st.dataframe(df_open_so)



    with st.spinner("Fetching RF Pick Data..."):
        df_rf_pick = process_netsuite_data_csv(st.secrets["url_rf_pick"])
    
    
    # Map the 'Ship Via' and 'Terms' columns using the defined dictionaries
    df_open_so['Ship Via'] = df_open_so['Ship Via'].map(ship_via_mapping).fillna('Unknown')
    df_open_so['Terms'] = df_open_so['Terms'].map(terms_mapping).fillna('Unknown')

    # Sidebar Sales Rep Filters
    st.sidebar.subheader("Filter by Sales Rep")
    sales_reps = ['All'] + sorted([sales_rep_mapping.get(rep_id, 'Unknown') for rep_id in df_open_so['Sales Rep'].unique()])
    selected_sales_reps = st.sidebar.multiselect("Select Sales Reps", sales_reps, default=['All'])

    # Sidebar Ship Via Filters
    st.sidebar.subheader("Filter by Ship Via")
    ship_vias = ['All'] + sorted(df_open_so['Ship Via'].unique())
    selected_ship_vias = st.sidebar.multiselect("Select Ship Via", ship_vias, default=['All'])

    # Task ID Filters
    filter_with_task_id = st.sidebar.checkbox("Show rows with Task ID", value=True)
    filter_without_task_id = st.sidebar.checkbox("Show rows without Task ID", value=True)

    # Ship Date Filter
    st.sidebar.subheader("Filter by Ship Date")
    date_preset = st.sidebar.selectbox("Select date range preset", ["Custom", "Today", "Tomorrow", "This Week", "This Month"])

    if date_preset == "Custom":
        min_date = pd.to_datetime(df_open_so['Ship Date']).min()
        max_date = pd.to_datetime(df_open_so['Ship Date']).max()
        selected_date_range = st.sidebar.date_input("Select custom date range", [min_date, max_date], min_value=min_date, max_value=max_date)
    else:
        start_date, end_date = get_date_range(date_preset)
        st.sidebar.write(f"Selected range: {start_date} to {end_date}")
        selected_date_range = [start_date, end_date]

    # Merge the dataframes
    merged_df = pd.merge(df_open_so, df_rf_pick[['Task ID', 'Order Number']].drop_duplicates(), on='Order Number', how='left')
    merged_df['Sales Rep'] = merged_df['Sales Rep'].replace(sales_rep_mapping)
    merged_df['Order Number'] = merged_df['Order Number'].astype(str)

    # Apply Sales Rep and Ship Via filters
    if 'All' not in selected_sales_reps:
        merged_df = merged_df[merged_df['Sales Rep'].isin(selected_sales_reps)]
    if 'All' not in selected_ship_vias:
        merged_df = merged_df[merged_df['Ship Via'].isin(selected_ship_vias)]

    # Apply Task ID filters
    if filter_with_task_id and not filter_without_task_id:
        merged_df = merged_df[merged_df['Task ID'].notna()]
    elif filter_without_task_id and not filter_with_task_id:
        merged_df = merged_df[merged_df['Task ID'].isna()]

    # Apply Ship Date filter
    merged_df['Ship Date'] = pd.to_datetime(merged_df['Ship Date'])
    merged_df = merged_df[(merged_df['Ship Date'] >= pd.to_datetime(selected_date_range[0])) & (merged_df['Ship Date'] <= pd.to_datetime(selected_date_range[1]))]

    # Calculate totals for tasked and untasked orders
    total_orders = len(merged_df)
    matched_orders = merged_df['Task ID'].notna().sum()
    unmatched_orders = merged_df['Task ID'].isna().sum()

    # Create and display the line chart for filtered data
    if not merged_df.empty:
        col_chart, col_pie = st.columns([2, 1])  # Allocate 2/3 space for chart and 1/3 for pie chart
        with col_chart:
            st.plotly_chart(create_ship_date_chart(merged_df), use_container_width=True)
        
        with col_pie:
            st.plotly_chart(create_pie_chart(matched_orders, unmatched_orders), use_container_width=True)

    else:
        st.write("No data available for the selected filters.")

    # Calculate Successful Task Percentage
    successful_task_percentage = (matched_orders / total_orders) * 100 if total_orders > 0 else 0

    # Display metric boxes in one row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Open Orders", total_orders)

    with col2:
        st.metric("Tasked Orders", matched_orders)

    with col3:
        st.metric("Untasked Orders", unmatched_orders)

    with col4:
        st.metric("Successful Task Percentage", f"{successful_task_percentage:.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)  # Add some vertical space

    # Display filtered data inside an expandable section
    with st.expander("View Data Table"):
        st.subheader("Filtered Data Table")
        st.write(f"Total records after filtering: {len(merged_df)}")
        st.dataframe(merged_df, height=400)

        # Download option for filtered data
        csv = merged_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name="filtered_sales_orders_with_task_id.csv",
            mime="text/csv",
        )

    # Add link to NetSuite open order report
    st.markdown(
        """
        <br>
        <a href="https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5065&saverun=T&whence=" target="_blank">Link to open order report in NetSuite</a>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
