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

# Add separate Year and Month columns while keeping the original 'Month' column
sales_by_month_data['Month'] = pd.to_datetime(sales_by_month_data['Month'], format='%Y-%m')

# Create separate 'Year' and 'Month' columns from the original 'Month' column
sales_by_month_data['Year'] = sales_by_month_data['Month'].dt.year
sales_by_month_data['Month_Num'] = sales_by_month_data['Month'].dt.month

# Display the DataFrame with new columns for Year and Month
st.write("Sales by Month Data with Year and Month Columns:", sales_by_month_data)

# Filter data for 2023 and 2024
sales_2023 = sales_by_month_data[sales_by_month_data['Year'] == 2023][['Month_Num', 'Billed Amount']]
sales_2024 = sales_by_month_data[sales_by_month_data['Year'] == 2024][['Month_Num', 'Billed Amount']]

# Merge the data on 'Month_Num' for comparison
sales_month_comparison = pd.merge(
    sales_2023.rename(columns={'Billed Amount': 'Billed Amount 2023'}), 
    sales_2024.rename(columns={'Billed Amount': 'Billed Amount 2024'}), 
    on='Month_Num', how='outer'
)

# Fill any missing values with 0 in case some months are missing from the data
sales_month_comparison.fillna(0, inplace=True)

# Visualization: Line chart for both 2023 and 2024 on the same Jan-Dec x-axis
st.header("Sales by Month (2023 vs 2024 - Same Jan-Dec x-axis)")

fig = px.line(sales_month_comparison, 
              x='Month_Num', 
              y=['Billed Amount 2023', 'Billed Amount 2024'], 
              title='Sales by Month (2023 vs 2024)',
              labels={'value': 'Billed Amount', 'Month_Num': 'Month'},
              markers=True)

# Customize the x-axis to show month names
fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    )
)

st.plotly_chart(fig)
