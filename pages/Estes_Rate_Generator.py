import streamlit as st
from utils.estes import get_bearer_token, get_freight_quote

# Streamlit page configuration
st.set_page_config(page_title="Estes LTL Shipment Rate Generator", page_icon="🚚", layout="wide")

# Page title
st.title("Estes LTL Shipment Rate Generator")

# Input fields for shipment details
st.header("Shipment Details")
pickup_zip = st.text_input("Pickup ZIP Code", max_chars=5, placeholder="Enter pickup ZIP code")
delivery_zip = st.text_input("Delivery ZIP Code", max_chars=5, placeholder="Enter delivery ZIP code")
weight = st.number_input("Weight (lbs)", min_value=1, placeholder="Enter total weight in lbs")
handling_units = st.number_input("Handling Units", min_value=1, placeholder="Enter number of handling units")

# Button to get quote
if st.button("Get Freight Quote"):
    # Get bearer token
    token = get_bearer_token()
    if token:
        # Get freight quote using the Estes API
        quote = get_freight_quote(token, pickup_zip, delivery_zip, weight, handling_units)
        if quote:
            # Display quote details
            st.subheader("Freight Quote Details")
            st.json(quote)
        else:
            st.warning("Failed to retrieve a freight quote. Check input values and try again.")
