import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import pandas as pd
import plotly.express as px

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

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

import streamlit as st
import pandas as pd
import plotly.express as px
from kpi.sales_by_rep import get_sales_by_rep
from kpi.sales_by_category import get_sales_by_category
from kpi.sales_by_month import get_sales_by_month
from kpi.website_sales_by_month import get_website_revenue_by_month

# Define a function to calculate KPIs based on grouped sales data
def calculate_kpis(df_grouped):
    # Calculate total revenue
    total_revenue = df_grouped.sum().sum()  # Sum across all months and years

    # Check if 'Orders' column exists and ensure it contains numeric values
    if 'Orders' in df_grouped.columns:
        df_grouped['Orders'] = pd.to_numeric(df_grouped['Orders'], errors='coerce').fillna(0)
        total_orders = df_grouped['Orders'].sum()
    else:
        total_orders = 0  # Default to 0 if 'Orders' column doesn't exist
    
    average_order_volume = total_revenue / total_orders if total_orders > 0 else 0
    
    # Set top_sales_rep as a placeholder or find the Sales Rep with highest revenue
    top_sales_rep = "Placeholder Rep" if 'Sales Rep' not in df_grouped.columns else df_grouped['Sales Rep'].mode().values[0]

    return total_revenue, total_orders, average_order_volume, top_sales_rep

# Create tabs for different KPIs
tabs = st.tabs(["Sales Dashboard", "Website & Amazon Sales"])

# =========================== Sales Dashboard Tab ===========================
with tabs[0]:
    # Page title and subtitle
    st.title("Sales Dashboard")
    st.subheader("Overview of sales performance metrics from 01/01/2023")

    # Load data for Sales by Month and get YoY variance
    chart_sales_by_month, net_difference, percentage_variance = get_sales_by_month()

    # Load data for Sales by Rep and calculate KPIs
    chart_sales_by_rep, df_grouped = get_sales_by_rep()

    # Check the structure of df_grouped to ensure it has data
    if df_grouped is not None and not df_grouped.empty:
        total_revenue, total_orders, average_order_volume, top_sales_rep = calculate_kpis(df_grouped)
    else:
        st.warning("Sales data is unavailable or empty.")
        total_revenue, total_orders, average_order_volume, top_sales_rep = 0, 0, 0, "N/A"

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

# =========================== Website & Amazon Sales Tab ===========================
with tabs[1]:
    # Load data for Website Revenue by Month and get grouped data
    chart_website_revenue_by_month, website_revenue_df_grouped = get_website_revenue_by_month()

    # Check if the website revenue data is available and structured correctly
    if website_revenue_df_grouped is not None and not website_revenue_df_grouped.empty:
        # Debugging: Inspect website_revenue_df_grouped
        st.write("Debug: Structure of website_revenue_df_grouped")
        st.write(website_revenue_df_grouped)

        # Ensure numeric columns and handle NaNs
        website_revenue_df_grouped = website_revenue_df_grouped.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Calculate KPIs for Website Sales
        website_total_revenue, website_total_orders, website_average_order_volume, top_website_sales_rep = calculate_kpis(website_revenue_df_grouped)
    else:
        st.warning("Website revenue data is unavailable or empty.")
        website_total_revenue, website_total_orders, website_average_order_volume, top_website_sales_rep = 0, 0, 0, "N/A"

    # Assuming we have another KPI function for Amazon Sales (similar to Website Revenue)
    # Replace with the actual function if it exists
    # For demonstration, reusing get_sales_by_month (modify with correct Amazon Sales function)
    chart_amazon_sales_by_month, amazon_sales_df_grouped = get_sales_by_month()

    # Calculate KPIs for Website Sales
    if website_revenue_df_grouped is not None:
        website_total_revenue, website_total_orders, website_average_order_volume, top_website_sales_rep = calculate_kpis(website_revenue_df_grouped)
    else:
        website_total_revenue, website_total_orders, website_average_order_volume, top_website_sales_rep = 0, 0, 0, "N/A"

    # Calculate KPIs for Amazon Sales
    if amazon_sales_df_grouped is not None:
        amazon_total_revenue, amazon_total_orders, amazon_average_order_volume, top_amazon_sales_rep = calculate_kpis(amazon_sales_df_grouped)
    else:
        amazon_total_revenue, amazon_total_orders, amazon_average_order_volume, top_amazon_sales_rep = 0, 0, 0, "N/A"

    # Define KPI metrics for Website & Amazon Sales
    website_metrics = [
        {"label": "Website Revenue", "value": f"${website_total_revenue:,.2f}", "change": 8.0, "positive": 8.0 > 0},
        {"label": "Website Orders", "value": website_total_orders, "change": 5.0, "positive": 5.0 > 0},
        {"label": "Avg Order Volume (Website)", "value": f"${website_average_order_volume:,.2f}", "change": 2.5, "positive": 2.5 > 0},
        {"label": "Top Website Sales Rep", "value": top_website_sales_rep, "change": 0.0, "positive": True},  # Placeholder
    ]

    amazon_metrics = [
        {"label": "Amazon Revenue", "value": f"${amazon_total_revenue:,.2f}", "change": 7.0, "positive": 7.0 > 0},
        {"label": "Amazon Orders", "value": amazon_total_orders, "change": 4.0, "positive": 4.0 > 0},
        {"label": "Avg Order Volume (Amazon)", "value": f"${amazon_average_order_volume:,.2f}", "change": 1.5, "positive": 1.5 > 0},
        {"label": "Top Amazon Sales Rep", "value": top_amazon_sales_rep, "change": 0.0, "positive": True},  # Placeholder
    ]

    # Display Website KPI metric boxes in a row
    st.subheader("Website Sales Metrics")
    col1, col2, col3, col4 = st.columns(4)
    for col, metric in zip([col1, col2, col3, col4], website_metrics):
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

    # Display Amazon KPI metric boxes in a row
    st.subheader("Amazon Sales Metrics")
    col1, col2, col3, col4 = st.columns(4)
    for col, metric in zip([col1, col2, col3, col4], amazon_metrics):
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

    # Visualizations for Website & Amazon Sales
    col1, col2 = st.columns(2)

    # Column 1: Website Revenue visualization
    with col1:
        st.plotly_chart(chart_website_revenue_by_month, use_container_width=True)
        with st.expander("Data - Website Revenue by Month"):
            df_website_revenue = fetch_restlet_data('customsearch4978')  # Fetch data if needed
            if not df_website_revenue.empty:
                st.dataframe(df_website_revenue)

    # Column 2: Amazon Sales visualization
    with col2:
        st.plotly_chart(chart_amazon_sales_by_month, use_container_width=True)
        with st.expander("Data - Amazon Sales by Month"):
            df_amazon_sales = fetch_restlet_data('customsearch5156')  # Fetch data if needed
            if not df_amazon_sales.empty:
                st.dataframe(df_amazon_sales)
