import requests
import json
import streamlit as st

# Function to create the FedEx request payload
def create_fedex_rate_request(trimmed_data):
    return {
        "accountNumber": {
            "value": st.secrets["fedex_account_number"]
        },
        "requestedShipment": {
            "shipper": {
                "address": {
                    "streetLines": ["10 FedEx Pkwy"],
                    "city": "Memphis",
                    "stateOrProvinceCode": "TN",
                    "postalCode": "38116",
                    "countryCode": "US"
                }
            },
            "recipient": {
                "address": {
                    "streetLines": ["1600 Pennsylvania Avenue NW"],  # Adjust to real address if needed
                    "city": trimmed_data.get("shipCity", "Washington"),  # Fallback to a default value
                    "stateOrProvinceCode": trimmed_data.get("shipState", "DC"),  # Fallback to default
                    "postalCode": trimmed_data.get("shipPostalCode", "20500"),  # Fallback to default
                    "countryCode": trimmed_data.get("shipCountry", "US")  # Fallback to default
                }
            },
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "shippingChargesPayment": {
                "paymentType": "SENDER"
            },
            "rateRequestTypes": ["ACCOUNT"],
            "requestedPackageLineItems": [
                {
                    "groupPackageCount": 1,
                    "weight": {
                        "units": "LB",
                        "value": trimmed_data.get("packageWeight", 50)  # Default if weight is missing
                    },
                    "dimensions": {
                        "length": 20,  # Uniform dimension (example)
                        "width": 20,   # Uniform dimension (example)
                        "height": 20,  # Uniform dimension (example)
                        "units": "IN"
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
