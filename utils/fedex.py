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
                    "streetLines": ["10 FedEx Pkwy"],  # Static address or pull dynamically if needed
                    "city": "Memphis",
                    "stateOrProvinceCode": "TN",
                    "postalCode": "38116",
                    "countryCode": "US"
                }
            },
            "recipient": {
                "address": {
                    "streetLines": ["1600 Pennsylvania Avenue NW"],  # Adjust or pull from sales order
                    "city": trimmed_data["shipCity"],
                    "stateOrProvinceCode": trimmed_data["shipState"],
                    "postalCode": trimmed_data["shipPostalCode"],
                    "countryCode": trimmed_data["shipCountry"]
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
                        "value": trimmed_data["packageWeight"]
                    },
                    "dimensions": {
                        "length": 20,  # Uniform dimension
                        "width": 20,   # Uniform dimension
                        "height": 20,  # Uniform dimension
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
    
    response = requests.post(fedex_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json()  # Return the FedEx rate quote response
    else:
        return {"error": f"Error fetching FedEx rate: {response.status_code}"}
