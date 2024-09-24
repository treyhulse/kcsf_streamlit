import pandas as pd
from utils.restlet import fetch_restlet_data

# KPI: Sales by Month
def get_sales_by_month():
    # Fetch the data from the saved search with ID 'customsearch5146'
    df = fetch_restlet_data('customsearch5146')

    if df.empty:
        return pd.DataFrame()

    # Only keep relevant columns: 'Period' (YYYY-MM) and 'Billed Amount'
    df = df[['Period', 'Billed Amount']]

    # Summing the Billed Amount per Period
    df_grouped = df.groupby('Period').sum().reset_index()
    return df_grouped
