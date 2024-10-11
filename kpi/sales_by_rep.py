import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Sales by Rep
@st.cache_data(ttl=4800)  # Cache the data for 20 minutes (TTL)
def get_sales_by_rep():
    df = fetch_restlet_data('customsearch4963')

    # Ensure 'Billed Amount' is numeric by removing any special characters and converting it to float
    df['Billed Amount'] = pd.to_numeric(df['Billed Amount'], errors='coerce')

    if df.empty:
        return None, None  # Return None for both values if no data is fetched

    # Group by 'Sales Rep' and sum the 'Billed Amount'
    df_grouped = df[['Sales Rep', 'Billed Amount', 'Orders']].groupby('Sales Rep').sum().reset_index()

    # Sort by 'Billed Amount' and limit to top 10 sales reps
    df_grouped = df_grouped.sort_values(by='Billed Amount', ascending=False).head(10)

    # Create a bar chart using Plotly
    fig = px.bar(df_grouped, x='Sales Rep', y='Billed Amount', title="Top 10 Sales by Sales Rep")
    fig.update_layout(xaxis_title="Sales Rep", yaxis_title="Billed Amount")
    
    return fig, df_grouped  # Return both the chart and the grouped DataFrame
