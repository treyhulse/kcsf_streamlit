import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Amazon Revenue by Month
@st.cache_data(ttl=300)  # Cache the data for 1 hour (TTL)
def get_amazon_revenue_by_month():
    # Fetch data from the custom search 'customsearch5156'
    df = fetch_restlet_data('customsearch5156')

    # Debugging: Check if the data is fetched correctly
    if df.empty:
        print("Debug: The fetched data is empty.")
        return None, None  # Return None for both values to match expected output

    # Ensure 'Billed Amount' is in the correct format for numerical calculations
    try:
        df['Billed Amount'] = df['Billed Amount'].replace('[\$,]', '', regex=True).astype(float)
    except Exception as e:
        print(f"Debug: Failed to convert 'Billed Amount' to float. Error: {e}")
        return None, None  # Return None for both values if conversion fails

    # Extract year and month from 'Period'
    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month

    # Group and pivot the data to get the total Billed Amount per month and year
    df_grouped = df.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Debugging: Print the structure of the grouped DataFrame
    print(f"Debug: Grouped DataFrame structure:\n{df_grouped.head()}")

    # Check if df_grouped is empty
    if df_grouped.empty:
        print("Debug: The grouped DataFrame is empty after pivot.")
        return None, None  # Return None for both values if the grouped data is empty

    # Create a line chart using Plotly
    try:
        fig = px.line(df_grouped, x=df_grouped.index, y=df_grouped.columns, title="Amazon Revenue by Month", markers=True)
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Billed Amount",
            xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
            legend_title="Year"
        )

        # Return the figure and the grouped DataFrame
        return fig, df_grouped

    except Exception as e:
        print(f"Debug: Failed to create the Plotly chart. Error: {e}")
        return None, None  # Return None for both values if chart creation fails
