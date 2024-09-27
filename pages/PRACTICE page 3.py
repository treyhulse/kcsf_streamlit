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
import json  # Import json for serialization
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
def parse_ship_address(ship_address, city, state, postal_code, country):
    return {
        "streetAddress": ship_address,
        "city": city,
        "state": state,
        "postalCode": postal_code,
        "country": country
    }

# Sidebar filters
st.sidebar.header("Filters")

# Title
st.title("Shipping Rate Quote Tool")

# Fetch sales order data from the new saved search
sales_order_data_raw = fetch_raw_data("customsearch5149")

# Check if data is available
if not sales_order_data_raw.empty:
    st.write("Sales Orders List")

    # Display all columns and create a combined column to display both Sales Order and Customer in the dropdown
    sales_order_data_raw['sales_order_and_customer'] = sales_order_data_raw.apply(
        lambda row: f"Order: {row['Sales Order']} - Customer: {row['Customer']}", axis=1
    )

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

            # Extract the required columns for the form and API request
            ship_address = selected_row['Shipping Address']
            ship_city = selected_row['Shipping City']
            ship_state = selected_row['Shipping State/Province']
            ship_postal_code = selected_row['Shipping Zip']
            ship_country = selected_row['Shipping Country Code']
            total_weight = selected_row['Total Weight']

            # Convert total_weight to float if it is a string
            try:
                total_weight = float(total_weight)
            except ValueError:
                total_weight = 50.0  # Default to 50.0 if conversion fails

            # Parsed address for use in FedEx request
            parsed_address = parse_ship_address(ship_address, ship_city, ship_state, ship_postal_code, ship_country)

            st.markdown("### Modify Shipping Information")

            with st.form("fedex_request_form"):
                # Create fields that can be adjusted before sending to FedEx
                ship_city = st.text_input("City", value=parsed_address.get("city", ""))
                ship_state = st.text_input("State", value=parsed_address.get("state", ""))
                ship_postal_code = st.text_input("Postal Code", value=parsed_address.get("postalCode", ""))
                ship_country = st.text_input("Country", value=parsed_address.get("country", "US"))
                
                # Use validated package weight in the number input field
                package_weight = st.number_input("Package Weight (LB)", min_value=0.1, value=total_weight)

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

            # Create an empty container to hold the selected option
            selected_shipping_option = None

            # Create a container for the cards and allow selection
            with st.container():
                for option in top_rate_options:
                    service_type = option.get('serviceType', 'N/A')
                    delivery_time = option.get('deliveryTimestamp', 'N/A')
                    net_charge = option['ratedShipmentDetails'][0]['totalNetCharge']
                    currency = option['ratedShipmentDetails'][0].get('currency', 'USD')

                    # Display as a selectable card
                    if st.button(f"{service_type}: ${net_charge} {currency}", key=service_type):
                        selected_shipping_option = {
                            "service_type": service_type,
                            "net_charge": net_charge,
                            "currency": currency
                        }
                        st.session_state['selected_shipping_option'] = selected_shipping_option

            # Display the selected shipping option
            if 'selected_shipping_option' in st.session_state:
                selected_option = st.session_state['selected_shipping_option']
                st.markdown(f"### Selected Shipping Option: {selected_option['service_type']} (${selected_option['net_charge']} {selected_option['currency']})")

                # Send the selected shipping option back to NetSuite using REST Web Services
                if st.button("Submit Shipping Option to NetSuite"):
                    netsuite_payload = {
                        "shipmethod": selected_option['service_type'],  # Use the correct field ID for Ship Via
                        "shippingcost": selected_option['net_charge'],  # Use the correct field ID for Shipping Cost
                        "id": selected_id  # Use the selected Sales Order ID for the POST request
                    }

                    # Debugging: Print the payload to ensure it's correct before the request
                    st.write("NetSuite Payload:", netsuite_payload)

                    # Serialize the payload to JSON string
                    json_payload = json.dumps(netsuite_payload)

                    # Make a POST request to update the sales order with shipping details in NetSuite
                    try:
                        # Use the 'data' parameter and pass the JSON string
                        update_response = make_netsuite_rest_api_request(
                            endpoint=f"salesOrder/{selected_id}", 
                            data=json_payload,  # Use 'data' with JSON string
                            method='PUT'
                        )
                        if update_response:
                            st.success(f"Shipping option '{selected_option['service_type']}' submitted successfully!")
                        else:
                            st.error("Failed to submit shipping option to NetSuite.")
                    except Exception as e:
                        st.error(f"Error updating NetSuite: {e}")
else:
    st.error("No sales orders available.")
