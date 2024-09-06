import streamlit as st
import pandas as pd
from utils.data_functions import get_saved_search_data

# Set up the page layout
st.title("Shipping Report")

# Fetch data from NetSuite
data = get_saved_search_data()

if data:
    # Convert to DataFrame for display
    df = pd.DataFrame(data)

    # Display the data dynamically in Streamlit
    st.dataframe(df)

    # Add filters if needed (optional)
    if not df.empty:
        st.write("Add filters and visualizations here as needed.")
else:
    st.error("No data available.")
