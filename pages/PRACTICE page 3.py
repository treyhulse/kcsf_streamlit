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
from utils.restlet import fetch_restlet_data
from utils.rest import make_netsuite_rest_api_request
from utils.fedex import get_fedex_rate_quote

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

# Function to parse shipAddress into components and convert country name to ISO code
def parse_ship_address(ship_address):
    address_lines = [line.strip() for line in ship_address.split('\n') if line.strip()]
    if len(address_lines) >= 3:
        street_address = " ".join(address_lines[:-2])
        city_state_postal = address_lines[-2]
        country = address_lines[-1]
        if country == "United States":
            country = "US"
        city_state_postal_split = city_state_postal.split()
        postal_code = city_state_postal_split[-1]
        state = city_state_postal_split[-2]
        city = " ".join(city_state_postal_split[:-2])
        return {
            "streetAddress": street_address,
            "city": city,
            "state": state,
            "postalCode": postal_code,
            "country": country
        }
    else:
        return {
            "streetAddress": "",
            "city": "",
            "state": "",
            "postalCode": "",
            "country": ""
        }

# Sidebar filters
st.sidebar.header("Filters")

# Title
st.title("Shipping Rate Quote Tool")

# Fetch sales order data from saved search
sales_order_data_raw = fetch_raw_data("customsearch5122")

# Create layout structure
if not sales_order_data_raw.empty:
    st.write("Sales Orders List")

    sales_order_data_raw['sales_order_and_customer'] = sales_order_data_raw.apply(
        lambda row: f"Order: {row['Sales Order']} - Customer: {row['Customer']}", axis=1)

    # Top row with two columns: Order Search (left) and Order Information (right)
    top_row = st.columns(2)

    # Left column: Order Search
    with top_row[0]:
        selected_order_info = st.selectbox(
            "Select a Sales Order by ID and Customer",
            sales_order_data_raw['sales_order_and_customer']
        )

        # Find the selected sales order row
        selected_row = sales_order_data_raw[sales_order_data_raw['sales_order_and_customer'] == selected_order_info].iloc[0]
        selected_id = selected_row['id']  # Extract the actual Sales Order ID for further processing

        st.write(f"Selected Sales Order ID: {selected_id}")

    # Right column: Order Information/Form to be sent to FedEx
    with top_row[1]:
        if selected_id:
            st.write(f"Fetching details for Sales Order ID: {selected_id}...")

            # Construct the endpoint URL with the selected sales order's 'id'
            endpoint = f"salesOrder/{selected_id}"
            sales_order_data = make_netsuite_rest_api_request(endpoint)

            if sales_order_data:
                st.markdown("### Modify Shipping Information")
                parsed_address = parse_ship_address(sales_order_data.get("shipAddress", ""))

                with st.form("fedex_request_form"):
                    # Create fields that can be adjusted before sending to FedEx
                    ship_city = st.text_input("City", value=parsed_address.get("city", ""))
                    ship_state = st.text_input("State", value=parsed_address.get("state", ""))
                    ship_postal_code = st.text_input("Postal Code", value=parsed_address.get("postalCode", ""))
                    ship_country = st.text_input("Country", value=parsed_address.get("country", "US"))
                    package_weight = st.number_input("Package Weight (LB)", min_value=0.1, value=sales_order_data.get("custbody128", 50.0))

                    # Submit button within the form
                    submitted = st.form_submit_button("Send to FedEx")
                    if submitted:
                        fedex_data = {
                            "shipCity": ship_city,
                            "shipState": ship_state,
                            "shipCountry": ship_country,
                            "shipPostalCode": ship_postal_code,
                            "packageWeight": package_weight
                        }
                        # Fetch FedEx rate quote using the modified data
                        fedex_quote = get_fedex_rate_quote(fedex_data)

                        if "error" not in fedex_quote:
                            st.success("FedEx quote fetched successfully!")
                            st.session_state['fedex_response'] = fedex_quote  # Store the response in session state
                        else:
                            st.error(fedex_quote["error"])

    # Bottom row: FedEx Shipping Options
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

            # Limit to the top options
            top_rate_options = sorted_rate_options[:8]

            st.write(f"Found {len(top_rate_options)} shipping options")

            for option in top_rate_options:
                service_type = option.get('serviceType', 'N/A')
                delivery_time = option.get('deliveryTimestamp', 'N/A')
                net_charge = option['ratedShipmentDetails'][0]['totalNetCharge']
                currency = option['ratedShipmentDetails'][0].get('currency', 'USD')

                # Display as card-like UI
                with st.expander(f"{service_type}: ${net_charge} {currency}"):
                    st.write(f"**Service Type**: {service_type}")
                    st.write(f"**Estimated Delivery Time**: {delivery_time}")
                    st.write(f"**Total Net Charge**: ${net_charge} {currency}")
else:
    st.error("No sales orders available.")
