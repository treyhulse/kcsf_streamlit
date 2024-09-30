import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Website Revenue by Month
@st.cache_data(ttl=300)  # Cache the data for 1 hour (TTL)
def get_website_revenue_by_month():
    # Fetch data from the custom search 'customsearch4978'
    df = fetch_restlet_data('customsearch4978')

    # Ensure 'Billed Amount' and 'Orders' columns are in the correct format
    df['Billed Amount'] = df['Billed Amount'].replace('[\$,]', '', regex=True).astype(float)
    df['Orders'] = pd.to_numeric(df['Orders'], errors='coerce').fillna(0)
    if df.empty:
        return None, None, 0, 0  # Return None, None for charts and 0, 0 for metrics

    # Calculate total revenue and total orders
    total_revenue = df['Billed Amount'].sum()
    total_orders = df['Orders'].sum()
    avg_order_volume = total_revenue / total_orders if total_orders > 0 else 0

    # Extract year and month from the 'Period' column
    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month

    # Group and pivot data to create a summary table of Billed Amount by month and year
    df_grouped = df.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Create a line chart using Plotly
    fig = px.line(df_grouped, x=df_grouped.index, y=df_grouped.columns, title="Website Revenue Amount by Month", markers=True)
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Billed Amount",
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        legend_title="Year"
    )

    return fig, df_grouped, total_orders, avg_order_volume
