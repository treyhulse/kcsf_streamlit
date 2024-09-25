import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

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

import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Sales by Rep
@st.cache_data(ttl=3600)  # Cache the data for 1 hour (TTL)
def get_sales_by_rep():
    df = fetch_restlet_data('customsearch4963')

    # Ensure 'Billed Amount' is numeric by removing any special characters and converting it to float
    df['Billed Amount'] = pd.to_numeric(df['Billed Amount'], errors='coerce')

    if df.empty:
        return None

    # Group by 'Sales Rep' and sum the 'Billed Amount'
    df_grouped = df[['Sales Rep', 'Billed Amount']].groupby('Sales Rep').sum().reset_index()

    # Sort by 'Billed Amount' and limit to top 10 sales reps
    df_grouped = df_grouped.sort_values(by='Billed Amount', ascending=False).head(10)

    # Create a bar chart using Plotly
    fig = px.bar(df_grouped, x='Sales Rep', y='Billed Amount', title="Top 10 Sales by Sales Rep")
    fig.update_layout(xaxis_title="Sales Rep", yaxis_title="Billed Amount")
    
    return fig, df_grouped

# Calculate the KPIs
def calculate_kpis(df_grouped):
    total_revenue = df_grouped['Billed Amount'].sum()
    total_orders = len(df_grouped)  # Assuming 1 row per order, or use another column
    average_order_volume = total_revenue / total_orders if total_orders > 0 else 0
    top_sales_rep = df_grouped.loc[df_grouped['Billed Amount'].idxmax(), 'Sales Rep']

    return total_revenue, total_orders, average_order_volume, top_sales_rep

# Load data and calculate KPIs
chart, df_grouped = get_sales_by_rep()
total_revenue, total_orders, average_order_volume, top_sales_rep = calculate_kpis(df_grouped)

# Placeholder percentage change values for demo purposes
percentage_change_orders = 5.0  # Change values as needed
percentage_change_sales = 7.5
percentage_change_average = 3.2
percentage_change_needed = 4.0

# Display dynamic metric boxes with arrows and sub-numbers
metrics = [
    {"label": "Total Revenue", "value": f"${total_revenue:,.2f}", "change": percentage_change_sales, "positive": percentage_change_sales > 0},
    {"label": "Total Orders", "value": total_orders, "change": percentage_change_orders, "positive": percentage_change_orders > 0},
    {"label": "Avg Order Volume", "value": f"${average_order_volume:,.2f}", "change": percentage_change_average, "positive": percentage_change_average > 0},
    {"label": "Top Sales Rep", "value": top_sales_rep, "change": "N/A", "positive": True},  # No percentage change for this one
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
            <p class="metric-change" style="color:{color};">{arrow} {metric['change']}%</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.write("")

# Display the chart for Sales by Rep
st.plotly_chart(chart, use_container_width=True)
