import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Sales by Category
@st.cache_data(ttl=4800)  # Cache the data for 20 minutes (TTL)
def get_sales_by_category():
    df = fetch_restlet_data('customsearch5145')
    df['Billed Amount'] = df['Billed Amount'].replace('[\$,]', '', regex=True).astype(float)
    if df.empty:
        return None

    df = df[['Category', 'Billed Amount']]
    df_grouped = df.groupby('Category').sum().reset_index()

    # Create a pie chart using Plotly
    fig = px.pie(df_grouped, values='Billed Amount', names='Category', title="Sales by Category", hole=0.3)
    return fig
