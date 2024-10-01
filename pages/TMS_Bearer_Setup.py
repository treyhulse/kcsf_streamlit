import streamlit as st
import pandas as pd
from utils.restlet import fetch_restlet_data  # Custom module for fetching data from NetSuite
from requests_oauthlib import OAuth1
import requests
import json
import time

# Function to parse shipAddress into components and convert country name to ISO code
def parse_ship_address(ship_address, city, state, postal_code, country):
    return {
        "streetAddress": ship_address,
        "city": city,
        "state": state,
        "postalCode": postal_code,
        "country": country
    }

# Function to make a PATCH request to NetSuite to update the Sales Order
def update_netsuite_sales_order(order_id, shipping_cost, ship_via, headers, auth):
    url = f"https://3429264.suitetalk.api.netsuite.com/services/rest/record/v1/salesOrder/{order_id}"
    payload = json.dumps({
        "shippingCost": shipping_cost,
        "shipMethod": {
            "id": ship_via
        }
    })
    
    response = requests.patch(url, headers=headers, data=payload, auth=auth)
    return response

# FedEx service rate code to NetSuite shipping method ID and name mapping
fedex_service_mapping = {
    "FEDEX_GROUND": {"netsuite_id": 36, "name": "Fed Ex Ground"},
    "FEDEX_EXPRESS_SAVER": {"netsuite_id": 3655, "name": "Fed Ex Express Saver"},
    "FEDEX_2_DAY": {"netsuite_id": 3657, "name": "Fed Ex 2Day"},
    "STANDARD_OVERNIGHT": {"netsuite_id": 3, "name": "FedEx Standard Overnight"},
    "PRIORITY_OVERNIGHT": {"netsuite_id": 3652, "name": "Fed Ex Priority Overnight"},
    "FEDEX_2_DAY_AM": {"netsuite_id": 3656, "name": "Fed Ex 2Day AM"},
    "FIRST_OVERNIGHT": {"netsuite_id": 3654, "name": "Fed Ex First Overnight"},
    "FEDEX_INTERNATIONAL_PRIORITY": {"netsuite_id": 7803, "name": "Fed Ex International Priority"},
    "FEDEX_FREIGHT_ECONOMY": {"netsuite_id": 16836, "name": "FedEx Freight Economy"},
    "FEDEX_FREIGHT_PRIORITY": {"netsuite_id": 16839, "name": "FedEx Freight Priority"},
    "FEDEX_INTERNATIONAL_GROUND": {"netsuite_id": 8993, "name": "FedEx International Ground"},
    "FEDEX_INTERNATIONAL_ECONOMY": {"netsuite_id": 7647, "name": "FedEx International Economy"},
}

# Function to get the NetSuite internal ID from the FedEx rate code
def get_netsuite_id(fedex_rate_code):
    return fedex_service_mapping.get(fedex_rate_code, {}).get("netsuite_id", "Unknown ID")

# Function to get the service name from the FedEx rate code
def get_service_name(fedex_rate_code):
    return fedex_service_mapping.get(fedex_rate_code, {}).get("name", "Unknown Service")

# Fetch FedEx rate quote using the session state token
def get_fedex_rate_quote(data):
    # Use the token stored in session state
    if 'fedex_token' not in st.session_state:
        st.error("FedEx token not available. Please refresh the token and try again.")
        return {"error": "FedEx token not available"}

    headers = {
        "Authorization": f"Bearer {st.session_state['fedex_token']}",
        "Content-Type": "application/json"
    }

    fedex_api_url = "https://apis.fedex.com/rate/v1/rates/quotes"  # Replace with the appropriate endpoint for your FedEx integration

    # Include the account number and rate request types in the payload
    payload = {
        "accountNumber": {
            "value": st.secrets["fedex_account_number"]
        },
        "requestedShipment": {
            "shipper": {
                "address": {
                    "postalCode": data['shipPostalCode'],
                    "countryCode": data['shipCountry']
                }
            },
            "recipient": {
                "address": {
                    "postalCode": "90210",  # Replace with recipient's postal code
                    "countryCode": "US"     # Replace with recipient's country code
                }
            },
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "rateRequestType": ["LIST", "ACCOUNT"],  # Request both LIST and ACCOUNT rates
            "packageCount": "1",
            "requestedPackageLineItems": [
                {
                    "groupPackageCount": 1,
                    "weight": {
                        "units": "LB",
                        "value": data['packageWeight']
                    },
                    "dimensions": {
                        "length": 12,
                        "width": 12,
                        "height": 12,
                        "units": "IN"
                    }
                }
            ]
        }
    }

    # Make the API request
    response = requests.post(fedex_api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to get rate quote: {response.status_code} - {response.text}"}



# Fetch sales order data from the new saved search
@st.cache_data(ttl=900)
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    df = fetch_restlet_data(saved_search_id)
    return df

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
