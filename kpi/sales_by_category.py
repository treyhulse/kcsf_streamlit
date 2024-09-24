import pandas as pd
from utils.restlet import fetch_restlet_data

# KPI: Sales by Category
def get_sales_by_category():
    # Fetch the data from the saved search with ID 'customsearch5145'
    df = fetch_restlet_data('customsearch5145')

    if df.empty:
        return pd.DataFrame()

    # Only keep relevant columns: 'Category' and 'Billed Amount'
    df = df[['Category', 'Billed Amount']]

    # Summing the Billed Amount per Category
    df_grouped = df.groupby('Category').sum().reset_index()
    return df_grouped
