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
    # Split the address by new lines
    address_lines = ship_address.split('\n')
    
    # Assume the format is:
    # Line 1: Name (ignored)
    # Line 2: Company (ignored)
    # Line 3: Street Address
    # Line 4: City, State Postal Code
    # Line 5: Country
    
    if len(address_lines) >= 5:
        street_address = address_lines[2]
        city_state_postal = address_lines[3].split()  # Split city, state, and postal code
        country = address_lines[4]
        
        # Convert full country name to ISO 2-letter code if needed
        if country == "United States":
            country = "US"
        
        # Extract city, state, and postal code (assumes postal code is always last)
        city = " ".join(city_state_postal[:-2])
        state = city_state_postal[-2]
        postal_code = city_state_postal[-1]
        
        return {
            "streetAddress": street_address,
            "city": city,
            "state": state,
            "postalCode": postal_code,
            "country": country
        }
    else:
        return {}


# Sidebar filters
st.sidebar.header("Filters")

# Title
st.title("Sales Order Summary")

# Fetch sales order data from saved search
sales_order_data_raw = fetch_raw_data("customsearch5122")

# Show the data in a table with a selectbox to choose a sales order based on ID
if not sales_order_data_raw.empty:
    st.write("Sales Orders List")
    
    # Allow user to select a sales order by ID (assuming 'id' is in the response)
    selected_id = st.selectbox(
        "Select a Sales Order by ID",
        sales_order_data_raw['id'].unique()  # Assuming 'id' is a column in the data
    )
    
    # Display the selected sales order row for reference
    st.write(f"Selected Sales Order ID: {selected_id}")
else:
    st.error("No sales orders available.")

# Step 3: Fetch and display detailed information for the selected sales order
if selected_id:
    st.write(f"Fetching details for Sales Order ID: {selected_id}...")
    
    # Construct the endpoint URL with the selected sales order's 'id'
    endpoint = f"salesOrder/{selected_id}"
    
    # Fetch the sales order details from the API
    sales_order_data = make_netsuite_rest_api_request(endpoint)
    
    if sales_order_data:
        # Trimmed data for the display (you can adjust fields based on the response)
        trimmed_data = {
            "id": sales_order_data.get("id"),
            "tranId": sales_order_data.get("tranId"),
            "orderStatus": sales_order_data.get("orderStatus", {}).get("refName"),
            "billAddress": sales_order_data.get("billAddress"),
            "shipAddress": sales_order_data.get("shipAddress"),
            "subtotal": sales_order_data.get("subtotal"),
            "total": sales_order_data.get("total"),
            "createdDate": sales_order_data.get("createdDate"),
            "salesRep": sales_order_data.get("salesRep", {}).get("refName"),
            "shippingMethod": sales_order_data.get("shipMethod", {}).get("refName"),
            "currency": sales_order_data.get("currency", {}).get("refName")
        }
        
        # Display the sales order data in a card-like format
        with st.expander(f"Sales Order #{trimmed_data['tranId']} (ID: {trimmed_data['id']})"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Order Information")
                st.write(f"**Status**: {trimmed_data['orderStatus']}")
                st.write(f"**Order ID**: {trimmed_data['id']}")
                st.write(f"**Transaction ID**: {trimmed_data['tranId']}")
                st.write(f"**Created Date**: {trimmed_data['createdDate']}")
            with col2:
                st.markdown("### Financial Information")
                st.write(f"**Subtotal**: ${trimmed_data['subtotal']}")
                st.write(f"**Total**: ${trimmed_data['total']}")
                st.write(f"**Currency**: {trimmed_data['currency']}")

            st.markdown("### Addresses")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Billing Address")
                st.write(trimmed_data['billAddress'])
            with col2:
                st.markdown("#### Shipping Address")
                st.write(trimmed_data['shipAddress'])

            st.markdown("### Other Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Sales Rep**: {trimmed_data['salesRep']}")
            with col2:
                st.write(f"**Shipping Method**: {trimmed_data['shippingMethod']}")
        
        # Option to view the full raw JSON response
        with st.expander("View Full Response"):
            st.json(sales_order_data)
    else:
        st.error(f"Unable to fetch details for Sales Order ID: {selected_id}.")

# Parse the shipping address for the FedEx API call
if sales_order_data:
    ship_address_str = sales_order_data.get("shipAddress", "")
    if ship_address_str:
        parsed_address = parse_ship_address(ship_address_str)
        
        # Prepare the data to send to FedEx API
        trimmed_data = {
            "shipCity": parsed_address.get("city"),
            "shipState": parsed_address.get("state"),
            "shipCountry": parsed_address.get("country"),
            "shipPostalCode": parsed_address.get("postalCode"),
            "packageWeight": sales_order_data.get("custbody128")  # Assuming this is the weight field
        }
    else:
        st.error("Shipping address not found in sales order data.")
    
    # Button to fetch FedEx rate quote
    if st.button("Get FedEx Rate Quote"):
        fedex_quote = get_fedex_rate_quote(trimmed_data)
        if "error" not in fedex_quote:
            # Sort rate options by price
            rate_options = fedex_quote.get('output', {}).get('rateReplyDetails', [])
            sorted_rate_options = sorted(rate_options, key=lambda x: x['ratedShipmentDetails'][0]['totalNetCharge']['amount'])

            st.write(f"Found {len(sorted_rate_options)} shipping options")

            # Display each shipping option in a card
            for option in sorted_rate_options:
                service_type = option['serviceType']
                delivery_time = option.get('deliveryTimestamp', 'N/A')
                net_charge = option['ratedShipmentDetails'][0]['totalNetCharge']['amount']
                currency = option['ratedShipmentDetails'][0]['totalNetCharge']['currency']

                # Display as card-like UI
                with st.expander(f"{service_type}: ${net_charge} {currency}"):
                    st.write(f"**Service Type**: {service_type}")
                    st.write(f"**Estimated Delivery Time**: {delivery_time}")
                    st.write(f"**Total Net Charge**: ${net_charge} {currency}")
        else:
            st.error(fedex_quote["error"])
