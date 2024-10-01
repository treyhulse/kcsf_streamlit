import requests
import json
import streamlit as st
from utils.connections import connect_to_netsuite
import time

# Function to create the FedEx request payload
def create_fedex_rate_request(trimmed_data):
    return {
        "accountNumber": {
            "value": st.secrets["fedex_account_number"]
        },
        "rateRequestControlParameters": {
            "returnTransitTimes": False,
            "servicesNeededOnRateFailure": True,
            "variableOptions": "FREIGHT_GUARANTEE",
            "rateSortOrder": "SERVICENAMETRADITIONAL"
        },
        "requestedShipment": {
            "shipper": {
                "address": {
                    "streetLines": ["7400 E 12th Street"],
                    "city": "Kansas City",
                    "stateOrProvinceCode": "MO",
                    "postalCode": "64126",
                    "countryCode": "US",
                    "residential": False
                }
            },
            "recipient": {
                "address": {
                    "streetLines": ["1600 Pennsylvania Avenue NW"],
                    "city": trimmed_data.get("shipCity", "Washington"),
                    "stateOrProvinceCode": trimmed_data.get("shipState", "DC"),
                    "postalCode": trimmed_data.get("shipPostalCode", "20500"),
                    "countryCode": trimmed_data.get("shipCountry", "US"),
                    "residential": False
                }
            },
            # Removed "serviceType" to let FedEx return all applicable services
            "preferredCurrency": "USD",  # Assuming USD
            "rateRequestType": ["ACCOUNT", "LIST"],  # Both account and list rates
            "shipDateStamp": "2024-09-25",  # Ensure this is dynamic based on the current date or future date
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "requestedPackageLineItems": [
                {
                    "subPackagingType": "BAG",  # Assuming a package type
                    "groupPackageCount": 1,
                    "weight": {
                        "units": "LB",
                        "value": trimmed_data.get("packageWeight", 50)  # Default weight if missing
                    },
                    "dimensions": {
                        "length": 20,
                        "width": 20,
                        "height": 20,
                        "units": "IN"
                    },
                    "declaredValue": {
                        "amount": "100",  # Default declared value if required
                        "currency": "USD"
                    }
                }
            ]
        }
    }


# Function to send the request to FedEx API
def get_fedex_rate_quote(trimmed_data):
    fedex_url = "https://apis.fedex.com/rate/v1/rates/quotes"

    # Get a valid token using the centralized function
    fedex_token = get_valid_fedex_token()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {fedex_token}"  # Use the valid token from session state
    }
    
    payload = create_fedex_rate_request(trimmed_data)
    
    # Print payload to debug
    st.write("FedEx Request Payload:", payload)
    
    response = requests.post(fedex_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json()  # Return the FedEx rate quote response
    else:
        st.error(f"Error fetching FedEx rate: {response.status_code}")
        st.write("Response details:", response.text)  # Print full response to debug
        return {"error": f"Error fetching FedEx rate: {response.status_code}"}



def update_sales_order_shipping_details(sales_order_id, shipping_cost, ship_method_id):
    # Get the NetSuite base URL and headers from the connection function
    netsuite_base_url, headers = connect_to_netsuite()
    
    # Construct the full NetSuite Sales Order URL
    url = f"{netsuite_base_url}/services/rest/record/v1/salesOrder/{sales_order_id}"
    
    # Create the payload with shipping cost and ship method ID
    payload = {
        "shippingCost": shipping_cost,
        "shipMethod": {
            "id": ship_method_id
        }
    }

    # Convert payload to JSON string
    json_payload = json.dumps(payload)

    # Make the PATCH request to update the sales order
    response = requests.patch(url, headers=headers, data=json_payload)

    # Check the response status
    if response.status_code == 200:
        return response.json()  # Return the updated sales order details
    else:
        st.error(f"Failed to update sales order: {response.status_code} - {response.text}")
        return None
    


# Function to get a valid FedEx bearer token, refreshing it if necessary
def get_valid_fedex_token():
    # Check if the token is already in session state or has expired
    if 'fedex_token' not in st.session_state or 'fedex_token_expiration' not in st.session_state:
        # Request a new token if none exists
        new_token, expires_in = get_fedex_bearer_token()
        st.session_state['fedex_token'] = new_token
        st.session_state['fedex_token_expiration'] = time.time() + expires_in - 60  # Subtract 60 seconds for safety margin
    elif time.time() > st.session_state['fedex_token_expiration']:
        # Refresh the token if it has expired
        new_token, expires_in = get_fedex_bearer_token()
        st.session_state['fedex_token'] = new_token
        st.session_state['fedex_token_expiration'] = time.time() + expires_in - 60  # Subtract 60 seconds for safety margin

    # Return the valid token
    return st.session_state['fedex_token']

# Function to retrieve a new bearer token from FedEx using client ID and secret from st.secrets
def get_fedex_bearer_token():
    url = "https://apis.fedex.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": st.secrets["fedex_id"],          # Use fedex_id from st.secrets
        "client_secret": st.secrets["fedex_secret"],  # Use fedex_secret from st.secrets
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token'], token_info['expires_in']
    else:
        raise Exception(f"Failed to get token: {response.status_code}, {response.text}")
