# Estes_Rate_Generator.py

import streamlit as st
from utils.estes_refresh import get_bearer_token

# Set up the Streamlit app title
st.title("Estes Bearer Token Management")

# Create a button to manually refresh the bearer token
if st.button("Refresh Bearer Token"):
    token = get_bearer_token()
    if token:
        st.success("Bearer Token Refreshed Successfully!")
        st.write("Bearer Token:", token)
    else:
        st.error("Failed to refresh bearer token. Check the logs for more information.")
