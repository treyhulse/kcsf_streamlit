import requests
import json
import streamlit as st

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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['fedex_token']}"
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



# Function to update NetSuite Sales Order with Shipping Method and Shipping Cost
def update_sales_order_shipping_details(sales_order_id, shipping_cost, ship_method_id):
    # Construct the NetSuite Sales Order URL
    url = f"https://{st.secrets['netsuite_account_id']}.suitetalk.api.netsuite.com/services/rest/record/v1/salesOrder/{sales_order_id}"
    
    # Create the payload with shipping cost and ship method ID
    payload = {
        "shippingCost": shipping_cost,
        "shipMethod": {
            "id": ship_method_id
        }
    }

    # Convert payload to JSON string
    json_payload = json.dumps(payload)

    # Set up headers with authorization
    headers = {
        "Content-Type": "application/json",
        "Prefer": "return-content",  # Optional, only if you want the updated record back
        "Authorization": f"Bearer {st.secrets['netsuite_token']}"
    }

    # Make the PATCH request to update the sales order
    response = requests.patch(url, headers=headers, data=json_payload)

    # Check the response status
    if response.status_code == 200:
        return response.json()  # Return the updated sales order details
    else:
        st.error(f"Failed to update sales order: {response.status_code} - {response.text}")
        return None
