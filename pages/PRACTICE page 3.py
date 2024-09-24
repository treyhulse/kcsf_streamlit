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

# Check user email for cache clear button
if user_email in ["treyhulse3@gmail.com", "trey.hulse@kcstorefixtures.com"]:
    if st.button("Clear Cache"):
        st.cache.clear()
        st.success("Cache cleared!")

################################################################################################

## AUTHENTICATED

################################################################################################


import pandas as pd
import streamlit as st
import plotly.express as px
from utils.restlet import fetch_restlet_data
import time
import logging

# Set up logging to monitor the status
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Streamlit progress bar
progress_bar = st.progress(0)

# Fetch data using the RESTlet function
saved_search_id = 'customsearch5108'

# Cache only the data fetching part (returning a DataFrame)
@st.cache(ttl=86400, allow_output_mutation=True)
def fetch_data(saved_search_id):
    logger.info(f"Fetching data for saved search ID: {saved_search_id}")
    data = fetch_restlet_data(saved_search_id)
    data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce')  # Convert 'Amount' to numeric
    data['Date'] = pd.to_datetime(data['Date'])  # Ensure 'Date' is datetime type
    return data

# Fetch data (outside of the cache)
df = fetch_data(saved_search_id)

# Sidebar filters for 'Sales Rep' and 'Date'
st.sidebar.header("Filter Data")
all_reps = ['All'] + list(pd.unique(df['Sales Rep']))
selected_rep = st.sidebar.multiselect("Select Sales Rep", options=all_reps, default='All')
selected_date = st.sidebar.date_input("Select Date Range", [])

# Filter data based on sidebar selections
if 'All' not in selected_rep:
    df = df[df['Sales Rep'].isin(selected_rep)]
if selected_date:
    df = df[(df['Date'] >= selected_date[0]) & (df['Date'] <= selected_date[1])]

# Simulate progress updates (this part is not cached)
for i in range(5):
    progress_bar.progress((i+1)*20)
    time.sleep(0.1)

# Finalize progress
progress_bar.progress(100)

if not df.empty:
    st.success(f"Data fetched successfully with {len(df)} records.")

    # Calculate metrics for the dashboard
    billed_orders = df[df['Status'] == 'Billed']
    pending_orders = df[df['Status'] == 'Pending']
    closed_orders = df[(df['Status'] == 'Closed') & (~df['Closed Order Reason'].isin(['Items moved to a different order', 'Other - See Notes']))]

    total_revenue = billed_orders['Amount'].sum()
    average_order_volume = billed_orders['Amount'].mean()
    open_orders = len(pending_orders)
    lost_revenue = closed_orders['Amount'].sum()

    # Metrics with potential for percentage change (dummy values here for illustration)
    percentage_change_revenue = 5  # Example: 5% increase
    percentage_change_average = -2  # Example: 2% decrease

    metrics = [
        {"label": "Total Revenue", "value": f"${total_revenue:,.2f}", "change": percentage_change_revenue, "positive": percentage_change_revenue > 0},
        {"label": "Avg Order Volume", "value": f"${average_order_volume:,.2f}", "change": percentage_change_average, "positive": percentage_change_average > 0},
        {"label": "Open Orders", "value": open_orders, "change": 0, "positive": True},
        {"label": "Lost Revenue", "value": f"${lost_revenue:,.2f}", "change": 0, "positive": False}
    ]

            # Display dynamic metric boxes with arrows and sub-numbers
    metrics = [
        {"label": "Total Revenue", "value": f"${total_revenue:,.2f}", "change": percentage_change_revenue, "positive": percentage_change_revenue > 0},
        {"label": "Avg Order Volume", "value": f"${average_order_volume:,.2f}", "change": percentage_change_average, "positive": percentage_change_average > 0},
        {"label": "Open Orders", "value": open_orders, "change": 0, "positive": True},
        {"label": "Lost Revenue", "value": f"${lost_revenue:,.2f}", "change": 0, "positive": False}

            # Styling for the boxes
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
            .metric-change {
                margin: 0;
                font-size: 14px;
            }
            </style>
            """, unsafe_allow_html=True)

            # First row: metrics
            col1, col2, col3, col4 = st.columns(4)

            for col, metric in zip([col1, col2, col3, col4], metrics):
                arrow = "↑" if metric["positive"] else "↓"
                color = "green" if metric["positive"] else "red"

                with col:
                    st.markdown(f"""
                    <div class="metrics-box">
                        <h3 class="metric-title">{metric['label']}</h3>
                        <p class="metric-value">{metric['value']}</p>
                        <p class="metric-change" style="color:{color};">{arrow} {metric['change']}%</p>
                    </div>
                    """, unsafe_allow_html=True)

    # Visualization: Yearly Comparison Line Chart
    this_year = df[df['Date'].dt.year == pd.to_datetime('today').year]
    last_year = df[df['Date'].dt.year == pd.to_datetime('today').year - 1]
    fig_line = px.line()
    fig_line.add_scatter(x=this_year['Date'].dt.month, y=this_year['Amount'], mode='lines', name='This Year')
    fig_line.add_scatter(x=last_year['Date'].dt.month, y=last_year['Amount'], mode='lines', name='Last Year')
    fig_line.update_layout(title='Yearly Sales Comparison', xaxis_title='Month', yaxis_title='Amount')

    # Display Dataframe
    with st.expander("View Dataframe"):
        st.dataframe(df)

    st.plotly_chart(fig_line)

else:
    logger.info("No data returned.")
    st.error("No data available or failed to load.")
