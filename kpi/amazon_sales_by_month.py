import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

@st.cache_data(ttl=300)  # Cache the data for 5 minutes (TTL)
def get_amazon_revenue_by_month():
    df = fetch_restlet_data('customsearch5156')

    if df.empty:
        return None, None, 0, 0  # Return 0s if no data is available

    # Ensure 'Billed Amount' and 'Orders' columns are in the correct format
    df['Billed Amount'] = df.get('Billed Amount', 0).replace('[\$,]', '', regex=True).astype(float).fillna(0)
    df['Orders'] = pd.to_numeric(df.get('Orders', 0), errors='coerce').fillna(0)

    # Calculate metrics
    amazon_total_revenue = df['Billed Amount'].sum()
    amazon_total_orders = df['Orders'].sum()  # Sum of 'Orders'
    amazon_avg_order_volume = amazon_total_revenue / amazon_total_orders if amazon_total_orders > 0 else 0

    # Extract year and month from 'Period'
    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month

    # Group and pivot the data for visualizations
    df_grouped = df.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Create line chart
    fig = px.line(df_grouped, x=df_grouped.index, y=df_grouped.columns, title="Amazon Revenue by Month", markers=True)
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Billed Amount",
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        legend_title="Year"
    )

    return fig, df_grouped, amazon_total_orders, amazon_avg_order_volume