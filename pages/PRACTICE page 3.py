import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.restlet import fetch_restlet_data
import pandas as pd
import plotly.express as px

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
import json
from utils.restlet import fetch_restlet_data
from utils.fedex import get_fedex_rate_quote
from utils.fedex import update_sales_order_shipping_details

@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Function to parse shipAddress into components and convert country name to ISO code
def parse_ship_address(ship_address, city, state, postal_code, country):
    return {
        "streetAddress": ship_address,
        "city": city,
        "state": state,
        "postalCode": postal_code,
        "country": country
    }

st.sidebar.header("Filters")

# Title
st.title("Shipping Rate Quote Tool")

# Fetch sales order data from the new saved search
sales_order_data_raw = fetch_raw_data("customsearch5149")

if not sales_order_data_raw.empty:
    st.write("Sales Orders List")

    sales_order_data_raw['sales_order_and_customer'] = sales_order_data_raw.apply(
        lambda row: f"Order: {row['Sales Order']} - Customer: {row['Customer']}", axis=1
    )

    top_row = st.columns(2)

    # Left column: Order Search
    with top_row[0]:
        selected_order_info = st.selectbox(
            "Select a Sales Order by ID and Customer",
            sales_order_data_raw['sales_order_and_customer']
        )

        selected_row = sales_order_data_raw[sales_order_data_raw['sales_order_and_customer'] == selected_order_info].iloc[0]
        selected_id = selected_row['id']
        st.write(f"Selected Sales Order ID: {selected_id}")

    # Right column: Order Information/Form to be sent to FedEx
    with top_row[1]:
        if selected_id:
            st.write(f"Fetching details for Sales Order ID: {selected_id}...")

            ship_address = selected_row['Shipping Address']
            ship_city = selected_row['Shipping City']
            ship_state = selected_row['Shipping State/Province']
            ship_postal_code = selected_row['Shipping Zip']
            ship_country = selected_row['Shipping Country Code']
            total_weight = selected_row['Total Weight']

            try:
                total_weight = float(total_weight)
            except ValueError:
                total_weight = 50.0

            parsed_address = parse_ship_address(ship_address, ship_city, ship_state, ship_postal_code, ship_country)

            st.markdown("### Modify Shipping Information")

            with st.form("fedex_request_form"):
                ship_city = st.text_input("City", value=parsed_address.get("city", ""))
                ship_state = st.text_input("State", value=parsed_address.get("state", ""))
                ship_postal_code = st.text_input("Postal Code", value=parsed_address.get("postalCode", ""))
                ship_country = st.text_input("Country", value=parsed_address.get("country", "US"))
                
                package_weight = st.number_input("Package Weight (LB)", min_value=0.1, value=total_weight)

                submitted = st.form_submit_button("Send to FedEx")
                if submitted:
                    fedex_data = {
                        "shipCity": ship_city,
                        "shipState": ship_state,
                        "shipCountry": ship_country,
                        "shipPostalCode": ship_postal_code,
                        "packageWeight": package_weight
                    }
                    fedex_quote = get_fedex_rate_quote(fedex_data)

                    if "error" not in fedex_quote:
                        st.success("FedEx quote fetched successfully!")
                        st.session_state['fedex_response'] = fedex_quote
                    else:
                        st.error(fedex_quote["error"])

    if 'fedex_response' in st.session_state and st.session_state['fedex_response']:
        fedex_quote = st.session_state['fedex_response']
        st.markdown("### Available Shipping Options")

        rate_options = fedex_quote.get('output', {}).get('rateReplyDetails', [])
        valid_rate_options = [
            option for option in rate_options
            if 'ratedShipmentDetails' in option and len(option['ratedShipmentDetails']) > 0
        ]

        if valid_rate_options:
            sorted_rate_options = sorted(valid_rate_options, key=lambda x: x['ratedShipmentDetails'][0]['totalNetCharge'])

            top_rate_options = sorted_rate_options[:8]

            st.write(f"Found {len(top_rate_options)} shipping options")

            selected_shipping_option = None

            with st.container():
                for option in top_rate_options:
                    service_type = option.get('serviceType', 'N/A')
                    delivery_time = option.get('deliveryTimestamp', 'N/A')
                    net_charge = option['ratedShipmentDetails'][0]['totalNetCharge']
                    currency = option['ratedShipmentDetails'][0].get('currency', 'USD')

                    if st.button(f"{service_type}: ${net_charge} {currency}", key=service_type):
                        selected_shipping_option = {
                            "service_type": service_type,
                            "net_charge": net_charge,
                            "currency": currency
                        }
                        st.session_state['selected_shipping_option'] = selected_shipping_option

            if 'selected_shipping_option' in st.session_state:
                selected_option = st.session_state['selected_shipping_option']
                st.markdown(f"### Selected Shipping Option: {selected_option['service_type']} (${selected_option['net_charge']} {selected_option['currency']})")

                if st.button("Submit Shipping Option to NetSuite"):
                    update_response = update_sales_order_shipping_details(
                        sales_order_id=selected_id,
                        shipping_cost=selected_option['net_charge'],
                        ship_method_id="36"
                    )

                    if update_response:
                        st.success(f"Shipping option '{selected_option['service_type']}' submitted successfully!")
                    else:
                        st.error("Failed to submit shipping option to NetSuite.")
else:
    st.error("No sales orders available.")
