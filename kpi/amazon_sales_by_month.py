import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Amazon Revenue by Month
@st.cache_data(ttl=4800)  # Cache the data for 20 minutes (TTL)
def get_amazon_revenue_by_month():
    # Fetch data from the custom search 'customsearch5156'
    df = fetch_restlet_data('customsearch5156')

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
    fig = px.line(df_pivot, x=df_pivot.index, y=df_pivot.columns, title="Amazon Revenue by Month", markers=True)

    # Calculate totals for Amazon Orders
    amazon_total_orders = df['Orders'].sum()
    amazon_total_revenue = df['Billed Amount'].sum()
    amazon_avg_order_volume = amazon_total_revenue / amazon_total_orders if amazon_total_orders > 0 else 0

    return fig, df_grouped, amazon_total_orders, amazon_avg_order_volume, amazon_total_revenue
