import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(page_title="Customer Support", 
                   layout="wide",)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Customer Support")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Customer Support'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
from utils.restlet import fetch_restlet_data
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Cache the raw data fetching process, reset cache every 2 minutes (120 seconds)
@st.cache_data(ttl=120)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Fetch raw data
customer_complaints_data = fetch_raw_data("customsearch5153")

# Display the customer complaints data in a dataframe
st.dataframe(customer_complaints_data)