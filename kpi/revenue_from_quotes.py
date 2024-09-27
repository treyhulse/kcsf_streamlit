import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Sales by Category
@st.cache_data(ttl=300)  # Cache the data for 1 hour (TTL)
def get_sales_by_category():
    df = fetch_restlet_data('customsearch5145')
    df['Billed Amount'] = df['Billed Amount'].replace('[\$,]', '', regex=True).astype(float)
    if df.empty:
        return None

