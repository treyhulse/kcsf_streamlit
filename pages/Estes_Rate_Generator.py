import streamlit as st
from utils.estes import get_freight_quote, refresh_token

# Streamlit page configuration
st.set_page_config(page_title="Estes LTL Shipment Rate Generator", page_icon="🚚", layout="wide")

# Page title
st.title("Estes LTL Shipment Rate Generator")

# Button to manually refresh bearer token
if st.button("Refresh Bearer Token"):
    refresh_token()

# Input fields for shipment details
st.header("Shipment Details")
pickup_zip = st.text_input("Pickup ZIP Code", value="23234", max_chars=5, placeholder="Enter pickup ZIP code")
delivery_zip = st.text_input("Delivery ZIP Code", value="90001", max_chars=5, placeholder="Enter delivery ZIP code")
weight = st.number_input("Weight (lbs)", value=1000, min_value=1, placeholder="Enter total weight in lbs")
handling_units = st.number_input("Handling Units", value=1, min_value=1, placeholder="Enter number of handling units")

# Button to get quote
if st.button("Get Freight Quote"):
    quote = get_freight_quote(pickup_zip, delivery_zip, weight, handling_units)
    if quote:
        st.subheader("Freight Quote Details")
        st.json(quote)
    else:
        st.warning("Failed to retrieve a freight quote. Check input values and try again.")
