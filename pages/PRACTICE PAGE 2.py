
import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Configure page layout
st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Order Management'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
from utils.mongo_connection import get_mongo_client, get_collection_data
from utils.suiteql import fetch_suiteql_data

# Step 1: Establish connections
client = get_mongo_client()

# Step 2: Fetch data from MongoDB and NetSuite
# Fetch inventory data using your updated query from NetSuite (example query)
inventory_query = """
SELECT 
    item.id AS item_id,
    item.itemid AS item_name,
    balance.location AS location_name,
    balance.quantityonhand AS quantity_on_hand,
    balance.quantityavailable AS quantity_available
FROM 
    item
JOIN 
    inventorybalance AS balance ON item.id = balance.item
WHERE 
    item.isinactive = 'F'
ORDER BY 
    item_name ASC;
"""
inventory_data = fetch_suiteql_data(inventory_query)

# Fetch sales data using SuiteQL from NetSuite (example query)
sales_query = """
SELECT 
    transaction.trandate,
    transaction.tranid,
    customer.entityid AS customer_name,
    item.itemid AS item_name,
    transactionline.quantity,
    transactionline.rate,
    transactionline.netamount AS line_total
FROM 
    transaction
JOIN 
    transactionline ON transaction.id = transactionline.transaction
JOIN 
    item ON transactionline.item = item.id
JOIN 
    customer ON transaction.entity = customer.id
WHERE 
    transaction.type = 'SalesOrd' 
    AND transaction.trandate >= TO_DATE('01/01/2023', 'MM/DD/YYYY')
ORDER BY 
    transaction.trandate DESC;
"""
sales_data = fetch_suiteql_data(sales_query)

# Step 3: Ensure matching column names between datasets for the merge
# In sales_data, 'itemid' is used, but in inventory_data it's 'item_id'
# Rename 'item_id' in inventory_data to 'itemid' for merging
inventory_data.rename(columns={'item_id': 'itemid'}, inplace=True)

# Merge data on 'itemid'
merged_data = pd.merge(inventory_data, sales_data, on='itemid', how='left')

# Step 4: Calculate key metrics
# Sales velocity: total quantity sold / number of sales days
merged_data['sales_velocity'] = merged_data.groupby('itemid')['quantity'].transform('sum') / len(merged_data['trandate'].unique())

# Calculate reorder point (example logic)
merged_data['reorder_point'] = merged_data['sales_velocity'] * 30  # 30-day average

# Calculate stock on hand and buffer stock (example logic)
merged_data['buffer_stock'] = merged_data['reorder_point'] * 0.2
merged_data['reorder_needed'] = merged_data['quantity_on_hand'] < (merged_data['reorder_point'] + merged_data['buffer_stock'])

# Step 5: Display the merged data and metrics in Streamlit
st.title("Warehouse Inventory Control and Purchase Recommendation")

# Key Metrics
st.metric("Total Inventory Value", merged_data['amount'].sum())
st.metric("Total Items Below Reorder Point", merged_data['reorder_needed'].sum())

# Recommended purchases DataFrame
recommended_purchases = merged_data[merged_data['reorder_needed'] == True][['item_name', 'quantity_on_hand', 'reorder_point', 'sales_velocity', 'buffer_stock']]
st.subheader("Recommended Items to Purchase")
st.dataframe(recommended_purchases)

# Visualization: Sales velocity over time
st.subheader("Sales Velocity by Item")
st.bar_chart(merged_data[['item_name', 'sales_velocity']].set_index('item_name'))

# Step 6: Add Forecasting using Exponential Moving Average (EMA)
merged_data['sales_forecast'] = merged_data['quantity'].ewm(span=30, adjust=False).mean()

# Visualization of sales forecast
st.subheader("Sales Forecast (Exponential Moving Average)")
st.line_chart(merged_data[['item_name', 'sales_forecast']].set_index('item_name'))

# Step 7: Smart Reorder Recommendation Logic with Lead Time and MOQ
# Assuming we have lead_time and min_order_quantity in the dataset
merged_data['reorder_quantity'] = (merged_data['reorder_point'] + merged_data['sales_forecast'] * merged_data['lead_time']) - merged_data['quantity_on_hand']
merged_data['reorder_quantity'] = merged_data[['reorder_quantity', 'min_order_quantity']].max(axis=1)

# Display updated recommendations
recommended_purchases = merged_data[merged_data['reorder_needed'] == True][['item_name', 'quantity_on_hand', 'reorder_point', 'sales_velocity', 'buffer_stock', 'reorder_quantity']]
st.subheader("Updated Reorder Recommendations")
st.dataframe(recommended_purchases)

# Step 8: Insights and Alerts
# Add a stockout risk column
merged_data['stockout_risk'] = merged_data['quantity_on_hand'] < merged_data['buffer_stock']

# Show items with stockout risk
st.subheader("Items at Risk of Stockout")
at_risk_items = merged_data[merged_data['stockout_risk'] == True][['item_name', 'quantity_on_hand', 'reorder_point', 'sales_velocity', 'buffer_stock']]
st.dataframe(at_risk_items)

# Alerts for overstock
merged_data['overstock_alert'] = merged_data['quantity_on_hand'] > (merged_data['reorder_point'] * 1.5)
overstock_items = merged_data[merged_data['overstock_alert'] == True][['item_name', 'quantity_on_hand', 'reorder_point']]
st.subheader("Overstock Items")
st.dataframe(overstock_items)

# Step 9: Scenario Analysis
st.sidebar.subheader("Scenario Analysis")
forecast_increase = st.sidebar.slider("Increase Forecast by (%)", min_value=0, max_value=100, value=10)
lead_time_change = st.sidebar.slider("Adjust Lead Time by (days)", min_value=-10, max_value=10, value=0)

# Adjust sales forecast and lead time in real-time
merged_data['adjusted_forecast'] = merged_data['sales_forecast'] * (1 + forecast_increase / 100)
merged_data['adjusted_lead_time'] = merged_data['lead_time'] + lead_time_change

# Recalculate reorder quantities based on adjusted values
merged_data['adjusted_reorder_quantity'] = (merged_data['reorder_point'] + merged_data['adjusted_forecast'] * merged_data['adjusted_lead_time']) - merged_data['quantity_on_hand']

# Display the results of the scenario analysis
st.subheader("Scenario Analysis: Adjusted Reordering Recommendations")
st.dataframe(merged_data[['item_name', 'quantity_on_hand', 'adjusted_reorder_quantity']])

