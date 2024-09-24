import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px

# KPI: Sales by Month
def get_sales_by_month():
    df = fetch_restlet_data('customsearch5146')
    if df.empty:
        return None

    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month
    df_grouped = df.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Create a line chart using Plotly
    fig = px.line(df_grouped, x=df_grouped.index, y=df_grouped.columns, title="Sales by Month", markers=True)
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Billed Amount",
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        legend_title="Year"
    )
    return fig
