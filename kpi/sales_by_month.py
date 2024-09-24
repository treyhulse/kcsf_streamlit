import pandas as pd
from utils.restlet import fetch_restlet_data
import matplotlib.pyplot as plt

# KPI: Sales by Month
def get_sales_by_month():
    df = fetch_restlet_data('customsearch5146')
    if df.empty:
        return pd.DataFrame()

    df = df[['Period', 'Billed Amount']]
    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month
    df_grouped = df.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Create a line chart
    plt.figure(figsize=(10, 6))
    for column in df_grouped.columns:
        plt.plot(df_grouped.index, df_grouped[column], marker='o', label=str(column))
    plt.xlabel('Month')
    plt.ylabel('Billed Amount')
    plt.title('Sales by Month')
    plt.xticks(df_grouped.index, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.legend(title='Year')
    plt.grid(True)
    return plt

