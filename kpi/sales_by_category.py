import pandas as pd
from utils.restlet import fetch_restlet_data
import matplotlib.pyplot as plt

# KPI: Sales by Category
def get_sales_by_category():
    df = fetch_restlet_data('customsearch5145')
    if df.empty:
        return pd.DataFrame()

    df = df[['Category', 'Billed Amount']]
    df_grouped = df.groupby('Category').sum().reset_index()

    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(df_grouped['Billed Amount'], labels=df_grouped['Category'], autopct='%1.1f%%', startangle=140)
    plt.title('Sales by Category')
    return plt

