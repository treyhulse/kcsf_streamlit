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

import streamlit as st
from kpi.sales_by_rep import get_sales_by_rep
from kpi.sales_by_category import get_sales_by_category
from kpi.sales_by_month import get_sales_by_month

st.title("Sales Dashboard")

# Display Sales by Rep
st.subheader("Sales by Rep")
sales_by_rep_chart = get_sales_by_rep()
if sales_by_rep_chart:
    st.plotly_chart(sales_by_rep_chart)

# Display Sales by Category
st.subheader("Sales by Category")
sales_by_category_chart = get_sales_by_category()
if sales_by_category_chart:
    st.plotly_chart(sales_by_category_chart)

# Display Sales by Month
st.subheader("Sales by Month")
sales_by_month_chart = get_sales_by_month()
if sales_by_month_chart:
    st.plotly_chart(sales_by_month_chart)
