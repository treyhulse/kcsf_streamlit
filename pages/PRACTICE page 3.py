import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import pandas as pd

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import plotly.express as px

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Add a button to clear the cache
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.success("Cache cleared successfully!")

# Sidebar filters
st.sidebar.header("Saved Searches")

# Fetch raw data for the new saved searches
sales_by_rep_data = fetch_raw_data("customsearch4963")
sales_by_category_data = fetch_raw_data("customsearch5145")
sales_by_month_data = fetch_raw_data("customsearch5146")

# Function to format 'Billed Amount' as currency
def format_currency(df, column_name):
    df[column_name] = df[column_name].apply(lambda x: "${:,.2f}".format(x))
    return df

# Format 'Billed Amount' column for each dataframe
sales_by_rep_data = format_currency(sales_by_rep_data, 'Amount')
sales_by_category_data = format_currency(sales_by_category_data, 'Amount')
sales_by_month_data = format_currency(sales_by_month_data, 'Amount')

# Display each saved search in a DataFrame
saved_searches = {
    "Sales by Sales Rep": sales_by_rep_data,
    "Sales by Category": sales_by_category_data,
    "Sales by Month": sales_by_month_data
}

for search_name, df in saved_searches.items():
    st.header(search_name)
    st.dataframe(df)

# Visualization: Sales by Sales Rep (Pie Chart)
st.header("Sales by Sales Rep (Pie Chart)")
fig_rep = px.pie(sales_by_rep_data, names='Sales Rep', values='Amount', title='Sales by Sales Rep')
st.plotly_chart(fig_rep)

# Visualization: Sales by Month (Stacked Line Chart)
st.header("Sales by Month (Stacked Line Chart)")
# Assuming the sales_by_month_data has 'Month', 'Year', and 'Billed Amount' columns
sales_by_month_data['Amount'] = sales_by_month_data['Amount'].replace('[\$,]', '', regex=True).astype(float)

# Filter data for 2023 and 2024
sales_2023 = sales_by_month_data[sales_by_month_data['Year'] == 2023]
sales_2024 = sales_by_month_data[sales_by_month_data['Year'] == 2024]

# Merge the two years of data for comparison
sales_month_comparison = pd.merge(sales_2023[['Month', 'Amount']], 
                                  sales_2024[['Month', 'Amount']], 
                                  on='Month', 
                                  suffixes=('_2023', '_2024'))

fig_month = px.line(sales_month_comparison, x='Month', y=['Amount_2023', 'Amount_2024'], 
                    title='Sales by Month (2023 vs 2024)', labels={'value': 'Amount', 'variable': 'Year'})
st.plotly_chart(fig_month)

# Visualization: Sales by Category (Bar Chart)
st.header("Sales by Category (Bar Chart)")
fig_category = px.bar(sales_by_category_data, x='Category', y='Amount', title='Sales by Category')
st.plotly_chart(fig_category)
