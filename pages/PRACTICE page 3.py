import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import pandas as pd
import plotly.express as px

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

# Ensure 'Billed Amount' is numeric
def ensure_numeric(df, column_name):
    df[column_name] = pd.to_numeric(df[column_name].replace('[\$,]', '', regex=True), errors='coerce')
    df[column_name].fillna(0, inplace=True)
    return df

sales_by_rep_data = ensure_numeric(sales_by_rep_data, 'Billed Amount')
sales_by_category_data = ensure_numeric(sales_by_category_data, 'Billed Amount')
sales_by_month_data = ensure_numeric(sales_by_month_data, 'Billed Amount')

# Drop unnecessary columns 'Grouped Category' and 'Grouped Rep' if they exist
if 'Grouped Category' in sales_by_category_data.columns:
    sales_by_category_data = sales_by_category_data.drop(columns=['Grouped Category'])

if 'Grouped Rep' in sales_by_rep_data.columns:
    sales_by_rep_data = sales_by_rep_data.drop(columns=['Grouped Rep'])

# Visualization: Sales by Month (Stacked Line Chart)
st.header("Sales by Month (Stacked Line Chart)")

# Convert 'Month' to a datetime object for proper sorting
sales_by_month_data['Month'] = pd.to_datetime(sales_by_month_data['Month'], format='%Y-%m')

# Extract the 'Year' from the 'Month' column and add it as a separate column
sales_by_month_data['Year'] = sales_by_month_data['Month'].dt.year

# Sort the data by 'Month' for proper plotting
sales_by_month_data = sales_by_month_data.sort_values(by='Month')

# Filter data for 2023 and 2024 based on the 'Year' extracted from the 'Month' column
sales_2023 = sales_by_month_data[sales_by_month_data['Year'] == 2023]
sales_2024 = sales_by_month_data[sales_by_month_data['Year'] == 2024]

if not sales_2023.empty and not sales_2024.empty:
    # Merge the two years of data for comparison
    sales_month_comparison = pd.merge(
        sales_2023[['Month', 'Billed Amount']].rename(columns={'Billed Amount': 'Billed Amount_2023'}), 
        sales_2024[['Month', 'Billed Amount']].rename(columns={'Billed Amount': 'Billed Amount_2024'}), 
        on='Month', how='outer'
    )

    # Create the line chart with both years
    fig_month = px.line(sales_month_comparison, x='Month', y=['Billed Amount_2023', 'Billed Amount_2024'], 
                        title='Sales by Month (2023 vs 2024)', labels={'value': 'Billed Amount', 'variable': 'Year'})

    st.plotly_chart(fig_month)
else:
    st.warning("No data available for both 2023 and 2024 in Sales by Month.")
