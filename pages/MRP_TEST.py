import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import pandas as pd
import plotly.express as px
from utils.fedex import get_valid_fedex_token

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
page_name = 'MRP'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################
import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import pandas as pd
from datetime import timedelta

# Caching with a 3-hour TTL (time-to-live)
@st.cache_data(ttl=timedelta(hours=3))
def load_data(file):
    return pd.read_csv(file)

def calculate_net_inventory(demand_supply_data, inventory_data):
    # Automatically infer 'Source Warehouse' for Transfer Orders
    demand_supply_data['Source Warehouse'] = demand_supply_data.apply(
        lambda row: 'KCSF-OM' if row['Order Type'] == 'Transfer Order' and row['Warehouse'] == '1'
        else '1' if row['Order Type'] == 'Transfer Order' and row['Warehouse'] == 'KCSF-OM'
        else None, axis=1
    )
    
    # Separate demand and supply transactions based on 'Order Type'
    demand_data = demand_supply_data[demand_supply_data['Order Type'] == 'Sales Order']
    supply_data = demand_supply_data[demand_supply_data['Order Type'] == 'Purchase Order']
    transfer_data = demand_supply_data[demand_supply_data['Order Type'] == 'Transfer Order']
    
    # Convert 'Total Quantity Ordered' to numeric, filling non-numeric entries with 0
    transfer_data['Total Quantity Ordered'] = pd.to_numeric(transfer_data['Total Quantity Ordered'], errors='coerce').fillna(0)
    
    # Add transfer order quantities to Total Demand for the Source Warehouse
    transfer_demand_adjustment = transfer_data.copy()
    transfer_demand_adjustment['Warehouse'] = transfer_demand_adjustment['Source Warehouse']
    transfer_demand_adjustment = transfer_demand_adjustment.groupby(['Item', 'Warehouse'])['Total Quantity Ordered'].sum().reset_index()
    transfer_demand_adjustment.rename(columns={'Total Quantity Ordered': 'Transfer Demand'}, inplace=True)

    # Aggregate demand and supply data by Item and Warehouse
    demand_agg = demand_data.groupby(['Item', 'Warehouse'])['Total Remaining Demand'].sum().reset_index()
    supply_agg = supply_data.groupby(['Item', 'Warehouse'])['Total Quantity Ordered'].sum().reset_index()
    
    # Rename columns for clarity
    demand_agg.rename(columns={'Total Remaining Demand': 'Total Demand'}, inplace=True)
    supply_agg.rename(columns={'Total Quantity Ordered': 'Incoming Supply'}, inplace=True)
    
    # Merge the demand, supply, and transfer adjustments into inventory data
    combined_data = pd.merge(inventory_data[['Item', 'Warehouse', 'On Hand']],
                             demand_agg, on=['Item', 'Warehouse'], how='outer')
    combined_data = pd.merge(combined_data, supply_agg, on=['Item', 'Warehouse'], how='outer')
    combined_data = pd.merge(combined_data, transfer_demand_adjustment, on=['Item', 'Warehouse'], how='outer')

    # Convert columns to numeric, handling errors and replacing NaN with 0
    combined_data['On Hand'] = pd.to_numeric(combined_data['On Hand'], errors='coerce').fillna(0)
    combined_data['Total Demand'] = pd.to_numeric(combined_data['Total Demand'], errors='coerce').fillna(0)
    combined_data['Incoming Supply'] = pd.to_numeric(combined_data['Incoming Supply'], errors='coerce').fillna(0)
    combined_data['Transfer Demand'] = pd.to_numeric(combined_data['Transfer Demand'], errors='coerce').fillna(0)
    
    # Update Total Demand to include Transfer Demand from Source Warehouse
    combined_data['Total Demand'] += combined_data['Transfer Demand']
    combined_data.drop(columns=['Transfer Demand'], inplace=True)
    
    # Calculate the current backordered quantity and net inventory
    combined_data['Current Backordered Quantity'] = combined_data.apply(
        lambda row: max(row['Total Demand'] - row['On Hand'], 0), axis=1
    )
    combined_data['Net Inventory'] = combined_data['On Hand'] + combined_data['Incoming Supply'] - combined_data['Total Demand']
    
    # Filter out rows where both 'On Hand' and 'Total Demand' are zero
    combined_data = combined_data[(combined_data['On Hand'] > 0) | (combined_data['Total Demand'] > 0)]
    
    # Reorder columns to make 'Net Inventory' the last column
    column_order = ['Item', 'Warehouse', 'On Hand', 'Total Demand', 'Incoming Supply', 'Current Backordered Quantity', 'Net Inventory']
    combined_data = combined_data[column_order]
    
    return combined_data


# Streamlit UI
st.title("Net Inventory by Item and Warehouse")

# Links for dataset sources
st.write("[Link to Item Demand Dataset Source](https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5192&saverun=T&whence=)")
st.write("[Link to Current Inventory Dataset Source](https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5196&saverun=T&whence=)")
st.write("[Link to All Transactions Dataset Source](https://3429264.app.netsuite.com/app/common/search/searchresults.nl?searchid=5197&saverun=T&whence=)")

# Upload files
demand_supply_file = st.file_uploader("Upload Demand Dataset", type=["csv"])
inventory_file = st.file_uploader("Upload Current Inventory Dataset", type=["csv"])
third_file = st.file_uploader("Upload All Transactions Dataset", type=["csv"])

# Process files if both are uploaded
if demand_supply_file and inventory_file:
    demand_supply_data = load_data(demand_supply_file)
    inventory_data = load_data(inventory_file)
    
    # Calculate Net Inventory
    net_inventory_df = calculate_net_inventory(demand_supply_data, inventory_data)
    
    # Display Results
    st.write("### Net Inventory by Item and Warehouse")
    st.dataframe(net_inventory_df)

# Process third file for filtering by 'Type' column and exact 'Item' search
if third_file:
    third_data = load_data(third_file)
    
    # Ensure 'Type' column is present
    if 'Type' in third_data.columns:
        # Select unique types for filtering options
        unique_types = third_data['Type'].unique()
        selected_type = st.selectbox("Select Type to Filter", options=["All"] + list(unique_types))
        
        # Filter data based on selected type
        if selected_type != "All":
            filtered_data = third_data[third_data['Type'] == selected_type]
        else:
            filtered_data = third_data

        # Add exact search filter for 'Item' column
        item_search = st.text_input("Search for exact 'Item'")
        if item_search:
            filtered_data = filtered_data[filtered_data['Item'] == item_search]
        
        st.write("### Filtered Data based on 'Type' and 'Item'")
        st.dataframe(filtered_data)
    else:
        st.error("The uploaded file does not contain a 'Type' column.")
