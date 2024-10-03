# pages/mrp_dashboard.py

import streamlit as st
import pandas as pd
from utils.mrp_master_df import create_master_dataframe

# Set up page title
st.title("MRP Dashboard")

# Fetch the master dataframe with caching
@st.cache_data(ttl=900)
def get_master_dataframe():
    try:
        return create_master_dataframe(st.secrets)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Fetch the master dataframe
master_df = get_master_dataframe()

# Check if the master_df is empty before proceeding
if master_df.empty:
    st.warning("No data available to display. Please check the data source or API configurations.")
else:
    # Multiselect for item type and vendor
    item_type_options = sorted(master_df['item type'].dropna().unique())
    selected_item_types = st.multiselect('Select Item Type', options=item_type_options)

    vendor_options = sorted(pd.concat([master_df['vendor'], master_df['vendor']]).dropna().unique())
    selected_vendors = st.multiselect('Select Vendor', options=vendor_options)

    # Filter the data based on selections
    filtered_df = master_df[
        (master_df['item type'].isin(selected_item_types) if selected_item_types else True) &
        (master_df['vendor'].isin(selected_vendors) if selected_vendors else True)
    ]

    # Display the filtered DataFrame
    st.dataframe(filtered_df)

    # Download button for the filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(label="Download Filtered Data as CSV", data=csv, file_name='filtered_inventory_data.csv', mime='text/csv')
