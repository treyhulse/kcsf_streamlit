import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

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
page_name = 'Sales'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
from kpi.sales_by_rep import get_sales_by_rep
from kpi.sales_by_category import get_sales_by_category
from kpi.sales_by_month import get_sales_by_month
import pandas as pd

# Mock data for example purposes
# You would replace these with your actual data sources
def get_sales_by_rep_data():
    return pd.DataFrame({
        'Sales Rep': ['Rep A', 'Rep B', 'Rep C'],
        'Sales': [1000, 1500, 1200]
    })

def get_sales_by_category_data():
    return pd.DataFrame({
        'Category': ['Category A', 'Category B', 'Category C'],
        'Sales': [2000, 1800, 2200]
    })

def get_sales_by_month_data():
    return pd.DataFrame({
        'Month': ['January', 'February', 'March'],
        'Sales': [5000, 5200, 4800]
    })

st.title("Sales Dashboard")

# Create three columns for the visualizations
col1, col2, col3 = st.columns(3)

# Column 1: Sales by Rep
with col1:
    st.markdown("### Sales by Rep")
    sales_by_rep_chart = get_sales_by_rep()
    if sales_by_rep_chart:
        st.plotly_chart(sales_by_rep_chart, use_container_width=True)
    
    # Show the data when clicked
    with st.expander("Drill Down - Sales by Rep"):
        st.dataframe(get_sales_by_rep_data())

# Column 2: Sales by Category
with col2:
    st.markdown("### Sales by Category")
    sales_by_category_chart = get_sales_by_category()
    if sales_by_category_chart:
        st.plotly_chart(sales_by_category_chart, use_container_width=True)
    
    # Show the data when clicked
    with st.expander("Drill Down - Sales by Category"):
        st.dataframe(get_sales_by_category_data())

# Column 3: Sales by Month
with col3:
    st.markdown("### Sales by Month")
    sales_by_month_chart = get_sales_by_month()
    if sales_by_month_chart:
        st.plotly_chart(sales_by_month_chart, use_container_width=True)
    
    # Show the data when clicked
    with st.expander("Drill Down - Sales by Month"):
        st.dataframe(get_sales_by_month_data())
