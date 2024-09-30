import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Amazon Revenue by Month
@st.cache_data(ttl=600)  # Cache the data for 10 minutes (TTL)
def get_amazon_revenue_by_month():
    # Fetch data from the custom search 'customsearch5156'
    df = fetch_restlet_data('customsearch5156')

    if df.empty:
        return None, None, 0, 0

    # Ensure 'Billed Amount' and 'Orders' columns are in the correct format
    df['Billed Amount'] = pd.to_numeric(df.get('Billed Amount', 0).replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df['Orders'] = pd.to_numeric(df.get('Orders', 0), errors='coerce').fillna(0)

    # Debugging: Print the values of 'Billed Amount' and 'Orders' columns before further processing
    st.write("Raw Billed Amounts: ", df['Billed Amount'].values)
    st.write("Raw Orders: ", df['Orders'].values)

    # Extract year and month for grouping
    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month

    # Group by 'Month' and 'Year' and include 'Orders' in the sum aggregation
    # Make sure not to include unwanted rows or duplicates during grouping
    df_grouped = df.groupby(['Month', 'Year']).agg({'Billed Amount': 'sum', 'Orders': 'sum'}).reset_index()

    # Ensure that the group-by operation did not multiply or duplicate the values
    st.write("Grouped Data:", df_grouped)

    # Calculate total revenue and ensure it matches the grouped data totals
    amazon_total_revenue = df_grouped['Billed Amount'].sum()  # Sum of 'Billed Amount' after grouping
    amazon_total_orders = df_grouped['Orders'].sum()  # Sum of 'Orders' after grouping

    # Debugging: Print the total calculated revenue and order values
    st.write(f"Amazon Total Revenue: {amazon_total_revenue}")
    st.write(f"Amazon Total Orders: {amazon_total_orders}")

    # Calculate average order volume
    amazon_avg_order_volume = amazon_total_revenue / amazon_total_orders if amazon_total_orders > 0 else 0

    # Pivot table for 'Billed Amount' visualization
    df_pivot = df_grouped.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Create a line chart for 'Billed Amount'
    fig = px.line(df_pivot, x=df_pivot.index, y=df_pivot.columns, title="Amazon Revenue by Month", markers=True)

    return fig, df_grouped, amazon_total_orders, amazon_avg_order_volume
