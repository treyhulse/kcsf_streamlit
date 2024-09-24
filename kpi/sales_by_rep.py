import pandas as pd
from utils.restlet import fetch_restlet_data
import matplotlib.pyplot as plt

# KPI: Sales by Rep
def get_sales_by_rep():
    df = fetch_restlet_data('customsearch4963')
    if df.empty:
        return pd.DataFrame()

    df = df[['Sales Rep', 'Billed Amount']]
    df_grouped = df.groupby('Sales Rep').sum().reset_index()

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(df_grouped['Sales Rep'], df_grouped['Billed Amount'], color='skyblue')
    plt.xlabel('Sales Rep')
    plt.ylabel('Billed Amount')
    plt.title('Sales by Sales Rep')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

