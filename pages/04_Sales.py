import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data

st.set_page_config(layout="wide")

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
page_name = 'Sales'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
from kpi.sales_by_rep import get_sales_by_rep
from kpi.sales_by_category import get_sales_by_category
from kpi.sales_by_month import get_sales_by_month
import pandas as pd
import plotly.express as px

# KPI: Sales by Month
@st.cache_data(ttl=300)  # Cache the data for 1 hour (TTL)
def get_sales_by_month():
    df = fetch_restlet_data('customsearch5146')
    df['Billed Amount'] = df['Billed Amount'].replace('[\$,]', '', regex=True).astype(float)
    if df.empty:
        return None, None

    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month
    df_grouped = df.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Calculate YoY variance between 2023 and 2024
    if 2023 in df_grouped.columns and 2024 in df_grouped.columns:
        net_difference = df_grouped[2024].sum() - df_grouped[2023].sum()
        percentage_variance = (net_difference / df_grouped[2023].sum()) * 100 if df_grouped[2023].sum() != 0 else 0
    else:
        net_difference = 0
        percentage_variance = 0

    # Create a line chart using Plotly
    fig = px.line(df_grouped, x=df_grouped.index, y=df_grouped.columns, title="Sales by Month", markers=True)
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Billed Amount",
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        legend_title="Year"
    )
    return fig, net_difference, percentage_variance

# Calculate KPIs based on grouped sales data
def calculate_kpis(df_grouped):
    total_revenue = df_grouped['Billed Amount'].sum()
    
    # Check if 'Orders' column exists and ensure it contains numeric values
    if 'Orders' in df_grouped.columns:
        df_grouped['Orders'] = pd.to_numeric(df_grouped['Orders'], errors='coerce').fillna(0)
        total_orders = df_grouped['Orders'].sum()
    else:
        total_orders = 0  # Default to 0 if 'Orders' column doesn't exist
    
    average_order_volume = total_revenue / total_orders if total_orders > 0 else 0
    top_sales_rep = df_grouped.loc[df_grouped['Billed Amount'].idxmax(), 'Sales Rep']
    
    return total_revenue, total_orders, average_order_volume, top_sales_rep

# Page title and subtitle
st.title("Sales Dashboard")
st.subheader("Overview of sales performance metrics from 01/01/2023")

# Load data for Sales by Month and get YoY variance
chart_sales_by_month, net_difference, percentage_variance = get_sales_by_month()

# Load data for Sales by Rep and calculate KPIs
chart_sales_by_rep, df_grouped = get_sales_by_rep()

if df_grouped is not None:
    total_revenue, total_orders, average_order_volume, top_sales_rep = calculate_kpis(df_grouped)

    # Placeholder percentage change values for demo purposes
    percentage_change_orders = 5.0  # Change values as needed
    percentage_change_sales = 7.5
    percentage_change_average = 3.2
    percentage_change_yoy = percentage_variance  # Use the calculated YoY variance

    # Display dynamic metric boxes with arrows and sub-numbers
    metrics = [
        {"label": "Total Revenue", "value": f"${total_revenue:,.2f}", "change": percentage_change_sales, "positive": percentage_change_sales > 0},
        {"label": "Total Orders", "value": total_orders, "change": percentage_change_orders, "positive": percentage_change_orders > 0},
        {"label": "Avg Order Volume", "value": f"${average_order_volume:,.2f}", "change": percentage_change_average, "positive": percentage_change_average > 0},
        {"label": "YoY Sales (Net)", "value": f"${net_difference:,.2f}", "change": percentage_change_yoy, "positive": net_difference > 0},
    ]

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
                <p class="metric-change" style="color:{color};">{arrow} {metric['change']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

    # Separation between metrics and visualizations
    st.write("")

# Create 3 columns for the visualizations and data frames
col1, col2, col3 = st.columns(3)

# Column 1: Sales by Rep visualization and DataFrame
with col1:
    st.plotly_chart(chart_sales_by_rep, use_container_width=True)
    with st.expander("Data - Sales by Rep"):
        st.dataframe(df_grouped)

# Column 2: Sales by Category visualization and DataFrame
chart_sales_by_category = get_sales_by_category()
if chart_sales_by_category:
    with col2:
        st.plotly_chart(chart_sales_by_category, use_container_width=True)
        with st.expander("Data - Sales by Category"):
            # Assuming you have a DataFrame for Sales by Category, you would display it here.
            df_sales_by_category = fetch_restlet_data('customsearch5145')  # Fetch data if needed
            if not df_sales_by_category.empty:
                st.dataframe(df_sales_by_category)

# Column 3: Sales by Month visualization and DataFrame
if chart_sales_by_month:
    with col3:
        st.plotly_chart(chart_sales_by_month, use_container_width=True)
        with st.expander("Data - Sales by Month"):
            # Assuming you have a DataFrame for Sales by Month, you would display it here.
            df_sales_by_month = fetch_restlet_data('customsearch5146')  # Fetch data if needed
            if not df_sales_by_month.empty:
                st.dataframe(df_sales_by_month)

            # Aggregate sales by year for 2023 and 2024
            df_sales_by_month['Year'] = pd.to_datetime(df_sales_by_month['Period']).dt.year
            yearly_sales = df_sales_by_month.groupby('Year')['Billed Amount'].sum().reset_index()
            yearly_sales.columns = ['Year', 'Total Billed Amount']

            # Column 3: Sales by Month visualization and DataFrame
            if chart_sales_by_month:
                with col3:
                    st.plotly_chart(chart_sales_by_month, use_container_width=True)
                    
                    # Original monthly sales data
                    with st.expander("Data - Sales by Month"):
                        if not df_sales_by_month.empty:
                            st.dataframe(df_sales_by_month)

                    # Aggregated yearly sales data
                    with st.expander("Total Sales by Year (2023 vs 2024)"):
                        st.dataframe(yearly_sales)

