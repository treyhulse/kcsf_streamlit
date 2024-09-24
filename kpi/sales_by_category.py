import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px

# KPI: Sales by Category
def get_sales_by_category():
    df = fetch_restlet_data('customsearch5145')
    if df.empty:
        return None

    df = df[['Category', 'Billed Amount']]
    df_grouped = df.groupby('Category').sum().reset_index()

    # Create a pie chart using Plotly
    fig = px.pie(df_grouped, values='Billed Amount', names='Category', title="Sales by Category", hole=0.3)
    return fig
