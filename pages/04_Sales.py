import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '04_Sales.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import logging
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# ... (previous code remains unchanged until the main Streamlit app section)

# Main Streamlit app
st.title('Sales Dashboard')

# MongoDB Connection
client = get_mongo_client()
sales_data = get_collection_data(client, 'sales')

# Apply global filters
sales_data = apply_global_filters(sales_data)

# Calculate KPIs
total_revenue, average_order_volume, total_open_estimates, total_open_orders = calculate_kpis(sales_data)

# Display KPIs in metric boxes
st.subheader('Key Performance Indicators')
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")

with col2:
    st.metric(label="Average Order Volume", value=f"${average_order_volume:,.2f}")

with col3:
    st.metric(label="Total Open Estimates", value=total_open_estimates)

with col4:
    st.metric(label="Total Open Orders", value=total_open_orders)

# Layout with columns for charts
col1, col2 = st.columns(2)

with col1:
    # Revenue by Sales Rep (Pie Chart)
    st.subheader('Revenue by Sales Rep')
    sales_rep_revenue = sales_data.groupby('Sales Rep')['Amount'].sum().reset_index()
    fig_pie = px.pie(sales_rep_revenue, names='Sales Rep', values='Amount', title='Revenue by Sales Rep')
    st.plotly_chart(fig_pie)

    # Sales by Category (Bar Graph)
    st.subheader('Sales by Category')
    sales_by_category = sales_data.groupby('Category')['Amount'].sum().reset_index()
    fig_bar = px.bar(sales_by_category, x='Category', y='Amount', title='Sales by Category')
    st.plotly_chart(fig_bar)

with col2:
    # Average Order Volume by Month and Sales Rep (Line Chart)
    st.subheader('Average Order Volume by Month and Sales Rep')
    
    # Ensure 'Date' is a datetime object and extract month
    sales_data['Date'] = pd.to_datetime(sales_data['Date'])
    sales_data['Month'] = sales_data['Date'].dt.to_period('M')
    
    # Calculate average order volume by month and sales rep
    avg_order_volume = sales_data.groupby(['Month', 'Sales Rep'])['Amount'].mean().reset_index()
    
    # Convert Period to datetime for plotting
    avg_order_volume['Month'] = avg_order_volume['Month'].dt.to_timestamp()
    
    # Create line chart
    fig_line = px.line(avg_order_volume, x='Month', y='Amount', color='Sales Rep',
                       title='Average Order Volume by Month and Sales Rep')
    fig_line.update_xaxes(title_text='Date')
    fig_line.update_yaxes(title_text='Average Order Volume')
    st.plotly_chart(fig_line)

    # Pipeline of Steps Based on 'Status'
    st.subheader('Pipeline by Status')
    status_pipeline = sales_data.groupby('Status').size().reset_index(name='count')
    fig_pipeline = px.funnel(status_pipeline, x='Status', y='count', title='Pipeline by Status')
    st.plotly_chart(fig_pipeline)

# Expandable AgGrid table at the bottom
with st.expander("View Data Table"):
    st.subheader("Sales Data")
    gb = GridOptionsBuilder.from_dataframe(sales_data)
    gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
    gridOptions = gb.build()

    grid_response = AgGrid(
        sales_data,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True,
        height=400, 
        width='100%',
        reload_data=True
    )