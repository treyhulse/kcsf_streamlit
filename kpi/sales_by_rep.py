import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Sales by Rep
@st.cache_data(ttl=3600)  # Cache the data for 1 hour (TTL)
def get_sales_by_rep():
    df = fetch_restlet_data('customsearch4963')
    df['Billed Amount'] = pd.to_numeric(df['Billed Amount'], errors='coerce')
    if df.empty:
        return None

    df = df[['Sales Rep', 'Billed Amount']]
    df_grouped = df.groupby('Sales Rep').sum().reset_index()

    # Create a bar chart using Plotly
    fig = px.bar(df_grouped, x='Sales Rep', y='Billed Amount', title="Sales by Sales Rep")
    fig.update_layout(xaxis_title="Sales Rep", yaxis_title="Billed Amount")
    return fig
