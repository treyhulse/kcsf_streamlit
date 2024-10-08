import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data

st.set_page_config(page_title="Sales", 
                   layout="wide",)

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
import pandas as pd
import plotly.express as px
from kpi.sales_by_rep import get_sales_by_rep
from kpi.sales_by_category import get_sales_by_category
from kpi.sales_by_month import get_sales_by_month
from kpi.website_sales_by_month import get_website_revenue_by_month
from kpi.amazon_sales_by_month import get_amazon_revenue_by_month
import html

# Define a function to calculate KPIs based on grouped sales data
def calculate_kpis(df_grouped):
    df_grouped = df_grouped.apply(pd.to_numeric, errors='coerce').fillna(0)
    total_revenue = df_grouped.sum().sum()
    if 'Orders' in df_grouped.columns:
        df_grouped['Orders'] = pd.to_numeric(df_grouped['Orders'], errors='coerce').fillna(0)
        total_orders = df_grouped['Orders'].sum()
    else:
        total_orders = 0  
    average_order_volume = total_revenue / total_orders if total_orders > 0 else 0
    top_sales_rep = "Placeholder Rep" if 'Sales Rep' not in df_grouped.columns else df_grouped['Sales Rep'].mode().values[0]
    return total_revenue, total_orders, average_order_volume, top_sales_rep

# Create the page title and subtitle outside of the tabs
st.title("Sales Dashboard")

# Create tabs for different KPIs as the main content
tab1, tab2 = st.tabs(["Sales", "Website and Amazon"])

# =========================== Sales Tab ===========================
with tab1:

    chart_sales_by_month, net_difference, percentage_variance = get_sales_by_month()
    chart_sales_by_rep, df_grouped = get_sales_by_rep()

    if df_grouped is not None and not df_grouped.empty:
        total_revenue, total_orders, average_order_volume, top_sales_rep = calculate_kpis(df_grouped)
    else:
        st.warning("Sales data is unavailable or empty.")
        total_revenue, total_orders, average_order_volume, top_sales_rep = 0, 0, 0, "N/A"
        net_difference = 0
        percentage_variance = 0

    percentage_change_orders = 5.0  
    percentage_change_sales = 7.5
    percentage_change_average = 3.2
    percentage_change_yoy = percentage_variance  

    try:
        net_difference = float(net_difference)
    except (ValueError, TypeError):
        net_difference = 0 

    metrics = [
        {"label": "Total Revenue", "value": f"${total_revenue:,.2f}", "change": percentage_change_sales, "positive": percentage_change_sales > 0},
        {"label": "Total Orders", "value": total_orders, "change": percentage_change_orders, "positive": percentage_change_orders > 0},
        {"label": "Avg Order Volume", "value": f"${average_order_volume:,.2f}", "change": percentage_change_average, "positive": percentage_change_average > 0},
        {"label": "YoY Sales (Net)", "value": f"${net_difference:,.2f}", "change": percentage_change_yoy, "positive": net_difference > 0},
    ]

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

    col1, col2, col3, col4 = st.columns(4)  

    for col, metric in zip([col1, col2, col3, col4], metrics):
        label = html.escape(metric['label'])
        value = html.escape(str(metric['value']))
        change = metric['change']  
        positive = metric['positive']
        arrow = "↑" if positive else "↓"
        color = "green" if positive else "red"

        with col:
            st.markdown(f"""
            <div class="metrics-box">
                <h3 class="metric-title">{label}</h3>
                <p class="metric-value">{value}</p>
                <p class="metric-change" style="color:{color};">{arrow} {change:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(chart_sales_by_rep, use_container_width=True)
        with st.expander("Sales by Rep"):
            st.dataframe(df_grouped)

    chart_sales_by_category = get_sales_by_category()
    if chart_sales_by_category:
        with col2:
            st.plotly_chart(chart_sales_by_category, use_container_width=True)
            with st.expander("Sales by Category"):
                df_sales_by_category = fetch_restlet_data('customsearch5145')
                if not df_sales_by_category.empty:
                    st.dataframe(df_sales_by_category)

    if chart_sales_by_month:
        with col3:
            st.plotly_chart(chart_sales_by_month, use_container_width=True)
            with st.expander("Sales by Month"):
                df_sales_by_month = fetch_restlet_data('customsearch5146')
                if not df_sales_by_month.empty:
                    st.dataframe(df_sales_by_month)


# =========================== Website and Amazon Tab ===========================

with tab2:
    # Initialize variables to ensure they are defined
    website_total_revenue, website_total_orders, website_avg_order_volume, amazon_total_revenue, amazon_total_orders, amazon_avg_order_volume = 0, 0, 0, 0, 0, 0

    # Retrieve data and KPI metrics with updated variable names
    chart_website_revenue_by_month, website_revenue_df_grouped, website_total_orders, website_avg_order_volume, website_total_revenue = get_website_revenue_by_month()
    chart_amazon_sales_by_month, amazon_sales_df_grouped, amazon_total_orders, amazon_avg_order_volume, amazon_total_revenue = get_amazon_revenue_by_month()

    # Metrics for Website and Amazon sections with formatted values
    website_metrics = [
        {"label": "Website Revenue", "value": f"${website_total_revenue:,.2f}", "change": 8.0, "positive": 8.0 > 0},
        {"label": "Website Orders", "value": f"{website_total_orders:,}", "change": 5.0, "positive": 5.0 > 0},
        {"label": "Avg Order Volume (Website)", "value": f"${website_avg_order_volume:,.2f}" if website_avg_order_volume else "$0.00", "change": 2.5, "positive": 2.5 > 0},
    ]

    amazon_metrics = [
        {"label": "Amazon Revenue", "value": f"${amazon_total_revenue:,.2f}", "change": 7.0, "positive": 7.0 > 0},
        {"label": "Amazon Orders", "value": f"{amazon_total_orders:,}", "change": 4.0, "positive": 4.0 > 0},
        {"label": "Avg Order Volume (Amazon)", "value": f"${amazon_avg_order_volume:,.2f}" if amazon_avg_order_volume else "$0.00", "change": 1.5, "positive": 1.5 > 0},
    ]

    # Display Website metrics in columns
    st.header("Website Metrics")
    col1, col2, col3 = st.columns(3)
    for col, metric in zip([col1, col2, col3], website_metrics):
        arrow = "↑" if metric["positive"] else "↓"
        color = "green" if metric["positive"] else "red"
        with col:
            st.markdown(f"""
            <div class="metrics-box">
                <h3 class="metric-title">{html.escape(metric['label'])}</h3>
                <p class="metric-value">{html.escape(str(metric['value']))}</p>
                <p class="metric-change" style="color:{color};">{arrow} {metric['change']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
    st.write("")
    
    # Display Website revenue chart and data
    st.plotly_chart(chart_website_revenue_by_month, use_container_width=True)
    with st.expander("Website Revenue by Month"):
        if website_revenue_df_grouped is not None and not website_revenue_df_grouped.empty:
            st.dataframe(website_revenue_df_grouped)
        else:
            st.warning("No website revenue data available for display.")

    # Display Amazon metrics in columns
    st.header("Amazon Metrics")
    col1, col2, col3 = st.columns(3)
    for col, metric in zip([col1, col2, col3], amazon_metrics):
        arrow = "↑" if metric["positive"] else "↓"
        color = "green" if metric["positive"] else "red"
        with col:
            st.markdown(f"""
            <div class="metrics-box">
                <h3 class="metric-title">{html.escape(metric['label'])}</h3>
                <p class="metric-value">{html.escape(str(metric['value']))}</p>
                <p class="metric-change" style="color:{color};">{arrow} {metric['change']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
    st.write("")

    # Display Amazon revenue chart and data
    st.plotly_chart(chart_amazon_sales_by_month, use_container_width=True)
    with st.expander("Amazon Revenue by Month"):
        if amazon_sales_df_grouped is not None and not amazon_sales_df_grouped.empty:
            st.dataframe(amazon_sales_df_grouped)
        else:
            st.warning("No Amazon revenue data available for display.")

    st.write("")

    st.header("Item Sales Margins")
    with st.expander("Item Sales Margins"):
        df_raw_sales_data = fetch_restlet_data('customsearch4990')
        if df_raw_sales_data is not None and not df_raw_sales_data.empty:
            if 'Average Shipping Cost Per Unit' in df_raw_sales_data.columns:
                # Convert the column to numeric, forcing errors to NaN (in case there are non-numeric values)
                df_raw_sales_data['Average Shipping Cost Per Unit'] = pd.to_numeric(
                    df_raw_sales_data['Average Shipping Cost Per Unit'], errors='coerce'
                ).round(2)
            st.dataframe(df_raw_sales_data)
        else:
            st.warning("No raw sales data available for display.")
