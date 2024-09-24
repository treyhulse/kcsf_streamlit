import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

from utils.restlet import fetch_restlet_data
import pandas as pd
import plotly.express as px


# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Sidebar filters
st.sidebar.header("Filters")

# Fetch raw data for estimates, sales orders, customsearch5128, customsearch5129, and quote data
estimate_data_raw = fetch_raw_data("customsearch5127")
sales_order_data_raw = fetch_raw_data("customsearch5122")
customsearch5128_data_raw = fetch_raw_data("customsearch5128")
customsearch5129_data_raw = fetch_raw_data("customsearch5129")
customsearch5132_data_raw = fetch_raw_data("customsearch5132")
quote_data_raw = fetch_raw_data("customsearch4993")

# Extract unique sales reps from both datasets and add 'All' option
unique_sales_reps = pd.concat([
    estimate_data_raw['Sales Rep'], 
    sales_order_data_raw['Sales Rep'],
    customsearch5128_data_raw['Sales Rep'],
    customsearch5129_data_raw['Sales Rep']
]).dropna().unique()
unique_sales_reps = ['All'] + sorted(unique_sales_reps)  # Add 'All' as the first option

# Sales rep filter in the sidebar
selected_sales_reps = st.sidebar.multiselect("Select Sales Reps", options=unique_sales_reps, default=['All'])

# Apply the filter dynamically (not cached) to both datasets
def apply_filters(df):
    if selected_sales_reps and 'All' not in selected_sales_reps:
        df = df[df['Sales Rep'].isin(selected_sales_reps)]
    return df

estimate_data = apply_filters(estimate_data_raw)
sales_order_data = apply_filters(sales_order_data_raw)
customsearch5128_data = apply_filters(customsearch5128_data_raw)
customsearch5129_data = apply_filters(customsearch5129_data_raw)
customsearch5132_data = customsearch5132_data_raw
quote_data = quote_data_raw  # Use raw data for quote

# Function to calculate metrics for orders or estimates
def calculate_metrics(df):
    total_records = df.shape[0]
    ready_records = df[(df['Payment Status'].isin(['Paid', 'Terms'])) & (df['Stock Status'] == 'In Stock')].shape[0]
    not_ready_records = total_records - ready_records
    
    # Safely convert 'Amount Remaining' to float, handling non-numeric values
    df['Amount Remaining'] = pd.to_numeric(df['Amount Remaining'], errors='coerce').fillna(0)
    
    outstanding_revenue = df['Amount Remaining'].sum()
    return total_records, ready_records, not_ready_records, outstanding_revenue

# Function to apply conditional formatting to the 'Sales Order' column only
def highlight_conditions_column(s):
    if s['Payment Status'] == 'Needs Payment':
        return ['color: red' if col == 'Sales Order' else '' for col in s.index]
    elif s['Stock Status'] == 'Back Ordered':
        return ['color: orange' if col == 'Sales Order' else '' for col in s.index]
    return [''] * len(s)  # No formatting otherwise

################################################################################################
st.header("Order Management")

# Function to count the records for each funnel stage
def calculate_funnel_stages(estimates_df, sales_orders_df):
    # Count of Estimates Open
    estimates_open = estimates_df.shape[0]

    # Count of Sales Orders Pending Fulfillment
    pending_fulfillment = sales_orders_df[sales_orders_df['Status'].isin(['Pending Fulfillment'])].shape[0]

    # Count of Sales Orders Partially Fulfilled AND Pending Billing/Partially Fulfilled
    partially_fulfilled = sales_orders_df[sales_orders_df['Status'].isin(['Partially Fulfilled', 'Pending Billing/Partially Fulfilled'])].shape[0]

    # Count of Sales Orders Ready (Filtered by Stock Status = 'In Stock' AND Payment Status = 'Paid' or 'Terms')
    ready_orders = sales_orders_df[(sales_orders_df['Stock Status'] == 'In Stock') & 
                                   (sales_orders_df['Payment Status'].isin(['Paid', 'Terms']))].shape[0]

    return estimates_open, pending_fulfillment, partially_fulfilled, ready_orders

# Get the counts for each funnel stage
estimates_open, pending_fulfillment, partially_fulfilled, ready_orders = calculate_funnel_stages(estimate_data, sales_order_data)

# Funnel Chart Data
funnel_data = pd.DataFrame({
    'stage': ['Estimates Open', 'Pending Fulfillment', 'Partially Fulfilled / Pending Billing', 'Orders Ready'],
    'amount': [estimates_open, pending_fulfillment, partially_fulfilled, ready_orders]
})

# Funnel Chart using Plotly
st.subheader("Sales Pipeline Funnel")
funnel_chart = px.funnel(funnel_data, x='stage', y='amount', text='amount',  # Show amounts instead of conversion
                         color_discrete_sequence=['firebrick'])  # Set the color to red

# Customize the appearance
funnel_chart.update_traces(texttemplate='%{text}', textposition="inside")
funnel_chart.update_layout(title_text='Sales Pipeline Funnel', title_x=0.5)

# Add the funnel chart to Streamlit
st.plotly_chart(funnel_chart)

################################################################################################

# Styling for the drop shadow boxes
st.markdown("""
<style>
.metrics-box {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
    text-align: center;
    margin-bottom: 20px;
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
.metric-change {
    margin: 0;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

def display_metrics(metrics):
    col1, col2, col3, col4 = st.columns(4)
    for idx, metric in enumerate(metrics):
        col = [col1, col2, col3, col4][idx]
        with col:
            change_class = "positive" if metric['positive'] else "negative"
            col.markdown(f"""
            <div class="metrics-box">
                <p class="metric-title">{metric['label']}</p>
                <p class="metric-value">{metric['value']}</p>
                <p class="metric-change" style="color: {'green' if metric['positive'] else 'red'}">
                    {metric['change']}%
                </p>
            </div>
            """, unsafe_allow_html=True)


# Subtabs for Estimates, Sales Orders, customsearch5128, customsearch5129, Work Orders
tab1, tab2, tab3, tab5, tab6 = st.tabs(["Sales Orders", "Estimates", "Purchase Orders", "Work Orders", "Transfer Orders"])

# Sales Orders tab (with metrics)
with tab1:
    st.subheader("Sales Orders")

    # Calculate metrics for sales orders
    total_orders, ready_orders, not_ready_orders, outstanding_revenue_orders = calculate_metrics(sales_order_data)
    
    # Placeholder percentage changes (you can replace these with actual calculations)
    percentage_change_orders = 100
    percentage_change_ready = round((ready_orders / total_orders) * 100, 1) if total_orders > 0 else 0
    percentage_change_not_ready = round((not_ready_orders / total_orders) * 100, 1) if total_orders > 0 else 0
    percentage_change_revenue = 15
    
    # Sales Orders Metrics
    sales_order_metrics = [
        {"label": "Total Orders", "value": total_orders, "change": percentage_change_orders, "positive": percentage_change_orders > 0},
        {"label": "Total Orders Ready", "value": ready_orders, "change": percentage_change_ready, "positive": percentage_change_ready > 0},
        {"label": "Total Orders Not Ready", "value": not_ready_orders, "change": percentage_change_not_ready, "positive": percentage_change_not_ready > 0},
        {"label": "Outstanding Revenue", "value": f"${outstanding_revenue_orders:,.2f}", "change": percentage_change_revenue, "positive": percentage_change_revenue > 0},
    ]
    
    display_metrics(sales_order_metrics)
    # Display the sales order data with conditional formatting
    st.dataframe(sales_order_data.style.apply(highlight_conditions_column, axis=1))

# Estimates tab (with the merged contents of Quote Data)
with tab2:
    st.subheader("Estimates")

    # Calculate metrics for estimates
    total_estimates, ready_estimates, not_ready_estimates, outstanding_revenue_estimates = calculate_metrics(estimate_data)

    # Convert 'Latest' and 'Earliest' to datetime with custom format in quote data
    quote_data['Latest'] = pd.to_datetime(quote_data['Latest'], format='%m/%d/%Y %I:%M %p', errors='coerce')
    quote_data['Earliest'] = pd.to_datetime(quote_data['Earliest'], format='%m/%d/%Y %I:%M %p', errors='coerce')

    # Calculate the time difference between 'Latest' and 'Earliest'
    quote_data['Time Difference'] = quote_data['Latest'] - quote_data['Earliest']

    # Calculate the average time difference
    avg_time_diff = quote_data['Time Difference'].mean()
    avg_time_diff_str = str(avg_time_diff).split('.')[0]  # Convert to string and remove microseconds

    # Placeholder percentage changes for estimates (you can replace these with actual calculations)
    percentage_change_estimates = 100
    percentage_change_ready_estimates = 8
    percentage_change_not_ready_estimates = -4
    percentage_change_revenue_estimates = 12

    # Estimates Metrics
    estimates_metrics = [
        {"label": "Total Estimates", "value": total_estimates, "change": percentage_change_estimates, "positive": percentage_change_estimates > 0},
        {"label": "Average Quote Cycle Time", "value": avg_time_diff_str, "change": percentage_change_ready_estimates, "positive": percentage_change_ready_estimates > 0},
        {"label": "Total Estimates Not Ready", "value": not_ready_estimates, "change": percentage_change_not_ready_estimates, "positive": percentage_change_not_ready_estimates > 0},
        {"label": "Outstanding Revenue", "value": f"${outstanding_revenue_estimates:,.2f}", "change": percentage_change_revenue_estimates, "positive": percentage_change_revenue_estimates > 0},
    ]

    display_metrics(estimates_metrics)
    # Display the estimate data with conditional formatting
    st.dataframe(estimate_data.style.apply(highlight_conditions_column, axis=1))

    # Nest the quote data DataFrame inside an expander
    with st.expander("View Detailed Quote Data"):
        st.dataframe(quote_data[['Document Number', 'Latest', 'Earliest', 'Time Difference']])

# Customsearch 5128 tab (no metrics)
with tab3:
    st.subheader("Purchase Orders")

    if not customsearch5128_data.empty:
        st.dataframe(customsearch5128_data)
    else:
        st.write("No data available for Customsearch 5128.")

# Customsearch 5132 tab (no metrics)
with tab5:
    st.subheader("Work Orders")

    if not customsearch5132_data.empty:
        st.dataframe(customsearch5132_data)
    else:
        st.write("No data available for Work Orders.")

# Customsearch 5129 tab (no metrics)
with tab6:
    st.subheader("Transfer Orders")

    if not customsearch5129_data.empty:
        st.dataframe(customsearch5129_data)
    else:
        st.write("No data available for Customsearch 5129.")

