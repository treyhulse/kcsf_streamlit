import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px

# KPI: Sales by Rep
def get_sales_by_rep():
    df = fetch_restlet_data('customsearch4963')
    if df.empty:
        return None

    df = df[['Sales Rep', 'Billed Amount']]
    df_grouped = df.groupby('Sales Rep').sum().reset_index()

    # Create a bar chart using Plotly
    fig = px.bar(df_grouped, x='Sales Rep', y='Billed Amount', title="Sales by Sales Rep")
    fig.update_layout(xaxis_title="Sales Rep", yaxis_title="Billed Amount")
    return fig
