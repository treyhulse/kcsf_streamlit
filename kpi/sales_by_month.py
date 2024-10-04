import pandas as pd
from utils.restlet import fetch_restlet_data
import plotly.express as px
import streamlit as st

# KPI: Sales by Month
@st.cache_data(ttl=1200)  # Cache the data for 20 minutes (TTL)
def get_sales_by_month():
    # Fetch data using the RESTlet ID 'customsearch5146'
    df = fetch_restlet_data('customsearch5146')

    # Debugging: Check if the data is fetched correctly
    if df.empty:
        print("Debug: The fetched data is empty.")
        return None, 0, 0  # Return None and two placeholder values for net_difference and percentage_variance

    # Ensure 'Billed Amount' is in the correct format for numerical calculations
    try:
        df['Billed Amount'] = df['Billed Amount'].replace('[\$,]', '', regex=True).astype(float)
    except Exception as e:
        print(f"Debug: Failed to convert 'Billed Amount' to float. Error: {e}")
        return None, 0, 0

    # Extract 'Year' and 'Month' from 'Period'
    df['Year'] = pd.to_datetime(df['Period']).dt.year
    df['Month'] = pd.to_datetime(df['Period']).dt.month

    # Group and pivot the data to get the total Billed Amount per month and year
    df_grouped = df.pivot_table(index='Month', columns='Year', values='Billed Amount', aggfunc='sum')

    # Debugging: Print the structure of the grouped DataFrame
    print(f"Debug: Grouped DataFrame structure:\n{df_grouped.head()}")

    # Check if df_grouped is empty
    if df_grouped.empty:
        print("Debug: The grouped DataFrame is empty after pivot.")
        return None, 0, 0

    # Calculate Year-over-Year (YoY) metrics if columns for 2023 and 2024 exist
    net_difference = 0
    percentage_variance = 0
    if 2023 in df_grouped.columns and 2024 in df_grouped.columns:
        net_difference = df_grouped[2024].sum() - df_grouped[2023].sum()
        percentage_variance = (net_difference / df_grouped[2023].sum()) * 100 if df_grouped[2023].sum() != 0 else 0

    # Create a line chart using Plotly
    try:
        fig = px.line(df_grouped, x=df_grouped.index, y=df_grouped.columns, title="Sales by Month", markers=True)
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Billed Amount",
            xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
            legend_title="Year"
        )

        # Debugging: Print the type of the generated figure
        print(f"Debug: Generated figure type: {type(fig)}")
        return fig, net_difference, percentage_variance  # Return three values: figure, net_difference, percentage_variance

    except Exception as e:
        print(f"Debug: Failed to create the Plotly chart. Error: {e}")
        return None, 0, 0

# Example use case to test in Streamlit
if __name__ == "__main__":
    st.title("Debug Sales by Month")
    sales_by_month_chart, net_diff, perc_var = get_sales_by_month()
    if sales_by_month_chart:
        st.plotly_chart(sales_by_month_chart)
    else:
        st.warning("Failed to generate the Sales by Month chart. Please check the logs for more information.")
