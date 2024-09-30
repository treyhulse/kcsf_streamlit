import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Website Revenue by Month
@st.cache_data(ttl=600)  # Cache the data for 10 minutes (TTL)
def get_website_revenue_by_month():
    # Fetch data from the custom search 'customsearch4978'
    df = fetch_restlet_data('customsearch4978')

    if df.empty:
        return None, None, 0, 0

    # Ensure 'Billed Amount' and 'Orders' columns are in the correct format
    df['Billed Amount'] = pd.to_numeric(df.get('Billed Amount', 0).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df['Orders'] = pd.to_numeric(df.get('Orders', 0), errors='coerce').fillna(0)

    # Extract year and month for grouping
    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month

    # Group by 'Month' and 'Year' and include 'Orders' in the sum aggregation
    df_grouped = df.groupby(['Month', 'Year']).agg({'Billed Amount': 'sum', 'Orders': 'sum'}).reset_index()

    # Pivot table for 'Billed Amount' visualization
    df_pivot = df_grouped.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Create a line chart for 'Billed Amount'
    fig = px.line(df_pivot, x=df_pivot.index, y=df_pivot.columns, title="Website Revenue by Month", markers=True)

    # Calculate totals for Website Orders
    website_total_orders = df['Orders'].sum()
    website_total_revenue = df['Billed Amount'].sum()
    website_avg_order_volume = website_total_revenue / website_total_orders if website_total_orders > 0 else 0

    return fig, df_grouped, website_total_orders, website_avg_order_volume, website_total_revenue