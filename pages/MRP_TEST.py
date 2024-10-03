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
        # Call the utility function to create the master DataFrame
        master_df = create_master_dataframe()
        return master_df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Fetch the master dataframe
master_df = get_master_dataframe()

# Check if the master_df is empty before proceeding
if master_df.empty:
    st.warning("No data available to display. Please check the data source or API configurations.")
else:
    st.success("Data loaded successfully.")
    
    # Display first few rows for verification
    st.write("Preview of the master data:")
    st.write(master_df.head())

    # Display column names for verification
    st.write("Column Names in Master DataFrame:")
    st.write(list(master_df.columns))  # Display column names for debugging

    # Multiselect for item type (no reference to vendor now)
    if 'item type' in master_df.columns:
        item_type_options = sorted(master_df['item type'].dropna().unique())
        selected_item_types = st.multiselect('Select Item Type', options=item_type_options)
    else:
        st.warning("'item type' column not found in the master DataFrame. Check if it exists in the raw data sources.")
        selected_item_types = []  # Empty selection if 'item type' is missing

    # Filter the data based on selected item types
    filtered_df = master_df[
        (master_df['item type'].isin(selected_item_types) if selected_item_types else True)
    ]

    # Display the filtered DataFrame
    st.dataframe(filtered_df)

    # Download button for the filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(label="Download Filtered Data as CSV", data=csv, file_name='filtered_inventory_data.csv', mime='text/csv')
