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
from kpi.sales_by_rep import get_sales_by_rep, fetch_restlet_data as fetch_rep_data
from kpi.sales_by_category import get_sales_by_category, fetch_restlet_data as fetch_category_data
from kpi.sales_by_month import get_sales_by_month, fetch_restlet_data as fetch_month_data
import pandas as pd

def format_currency(df, column_name):
    # Ensure the column is numeric, and fill any NaN values with 0
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce').fillna(0)
    
    # Apply currency formatting
    df[column_name] = df[column_name].apply(lambda x: "${:,.2f}".format(x))
    
    return df


st.title("Sales Dashboard")

# Create three columns for the visualizations
col1, col2, col3 = st.columns(3)

# Column 1: Sales by Rep
with col1:
    st.markdown("### Sales by Rep")
    sales_by_rep_chart = get_sales_by_rep()
    if sales_by_rep_chart:
        st.plotly_chart(sales_by_rep_chart, use_container_width=True)
    
    # Show the DataFrame for Sales by Rep when expanded
    with st.expander("Drill Down - Sales by Rep"):
        df_sales_by_rep = fetch_rep_data('customsearch4963')
        if 'Billed Amount' in df_sales_by_rep.columns:
            df_sales_by_rep = format_currency(df_sales_by_rep, 'Billed Amount')
        st.dataframe(df_sales_by_rep)

# Column 2: Sales by Category
with col2:
    st.markdown("### Sales by Category")
    sales_by_category_chart = get_sales_by_category()
    if sales_by_category_chart:
        st.plotly_chart(sales_by_category_chart, use_container_width=True)
    
    # Show the DataFrame for Sales by Category when expanded
    with st.expander("Drill Down - Sales by Category"):
        df_sales_by_category = fetch_category_data('customsearch5145')
        if 'Billed Amount' in df_sales_by_category.columns:
            df_sales_by_category = format_currency(df_sales_by_category, 'Billed Amount')
        st.dataframe(df_sales_by_category)

# Column 3: Sales by Month
with col3:
    st.markdown("### Sales by Month")
    sales_by_month_chart = get_sales_by_month()
    if sales_by_month_chart:
        st.plotly_chart(sales_by_month_chart, use_container_width=True)
    
    # Show the DataFrame for Sales by Month when expanded
    with st.expander("Drill Down - Sales by Month"):
        df_sales_by_month = fetch_month_data('customsearch5146')
        if 'Billed Amount' in df_sales_by_month.columns:
            df_sales_by_month = format_currency(df_sales_by_month, 'Billed Amount')
        st.dataframe(df_sales_by_month)
