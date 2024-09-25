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

st.title("Sales Dashboard")

# Create three columns for the visualizations
col1, col2, col3 = st.columns(3)

# Column 1: Sales by Rep
with col1:
    st.markdown("### Sales by Rep")
    sales_by_rep_chart = get_sales_by_rep()
    if sales_by_rep_chart:
        st.plotly_chart(sales_by_rep_chart, use_container_width=True)
    st.markdown("[Drill Down](https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=4963&whence=)")

# Column 2: Sales by Category
with col2:
    st.markdown("### Sales by Category")
    sales_by_category_chart = get_sales_by_category()
    if sales_by_category_chart:
        st.plotly_chart(sales_by_category_chart, use_container_width=True)
    st.markdown("[Drill Down](https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5145&whence=)")

# Column 3: Sales by Month
with col3:
    st.markdown("### Sales by Month")
    sales_by_month_chart = get_sales_by_month()
    if sales_by_month_chart:
        st.plotly_chart(sales_by_month_chart, use_container_width=True)
    st.markdown("[Drill Down](https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5146&whence=)")

# Anchors for each section to allow drill-down
st.markdown("<a name='sales-by-rep'></a>", unsafe_allow_html=True)
st.markdown("<a name='sales-by-category'></a>", unsafe_allow_html=True)
st.markdown("<a name='sales-by-month'></a>", unsafe_allow_html=True)
