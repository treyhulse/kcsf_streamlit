import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Amazon Revenue by Month
@st.cache_data(ttl=600)  # Cache the data for 10 minutes (TTL)
def get_amazon_revenue_by_month():
    df = fetch_restlet_data('customsearch5156')

    if df.empty:
        return None, None, 0, 0

    # Debug: Print raw data fetched
    print("Raw data fetched:", df.head())

    df['Billed Amount'] = pd.to_numeric(df.get('Billed Amount', 0).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df['Orders'] = pd.to_numeric(df.get('Orders', 0), errors='coerce').fillna(0)

    # Debug: Check the sum calculations
    amazon_total_revenue = df['Billed Amount'].sum()
    print("Total Revenue Calculated:", amazon_total_revenue)

    amazon_total_orders = df['Orders'].sum()
    df_grouped = df.groupby(['Month', 'Year']).agg({'Billed Amount': 'sum', 'Orders': 'sum'}).reset_index()
    df_pivot = df_grouped.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    amazon_avg_order_volume = amazon_total_revenue / amazon_total_orders if amazon_total_orders > 0 else 0

    return px.line(df_pivot, x=df_pivot.index, y=df_pivot.columns, title="Amazon Revenue by Month"), df_grouped, amazon_total_orders, amazon_avg_order_volume
