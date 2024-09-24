import pandas as pd
from utils.restlet import fetch_restlet_data

# KPI: Sales by Rep
def get_sales_by_rep():
    # Fetch the data from the saved search with ID 'customsearch4963'
    df = fetch_restlet_data('customsearch4963')

    if df.empty:
        return pd.DataFrame()

    # Only keep relevant columns: 'Sales Rep' and 'Billed Amount'
    df = df[['Sales Rep', 'Billed Amount']]

    # Summing the Billed Amount per Sales Rep
    df_grouped = df.groupby('Sales Rep').sum().reset_index()
    return df_grouped
