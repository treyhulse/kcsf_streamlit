import streamlit as st
from utils.estes import get_bearer_token, get_freight_quote

# Streamlit page configuration
st.set_page_config(page_title="Estes LTL Shipment Rate Generator", page_icon="🚚", layout="wide")

# Page title
st.title("Estes LTL Shipment Rate Generator")

# Pre-fill default values for testing
default_pickup_zip = "23234"   # Example ZIP code for pickup (Richmond, VA)
default_delivery_zip = "90001" # Example ZIP code for delivery (Los Angeles, CA)
default_weight = 1000          # Default weight in lbs
default_handling_units = 1     # Default handling units

# Input fields for shipment details
st.header("Shipment Details")
pickup_zip = st.text_input("Pickup ZIP Code", value=default_pickup_zip, max_chars=5, placeholder="Enter pickup ZIP code")
delivery_zip = st.text_input("Delivery ZIP Code", value=default_delivery_zip, max_chars=5, placeholder="Enter delivery ZIP code")
weight = st.number_input("Weight (lbs)", value=default_weight, min_value=1, placeholder="Enter total weight in lbs")
handling_units = st.number_input("Handling Units", value=default_handling_units, min_value=1, placeholder="Enter number of handling units")

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
