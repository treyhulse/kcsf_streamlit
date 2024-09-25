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
                    "streetLines": ["1600 Pennsylvania Avenue NW"],  # Use proper address
                    "city": trimmed_data.get("shipCity", "Washington"),
                    "stateOrProvinceCode": trimmed_data.get("shipState", "DC"),
                    "postalCode": trimmed_data.get("shipPostalCode", "20500"),
                    "countryCode": trimmed_data.get("shipCountry", "US")
                }
            },
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "shippingChargesPayment": {
                "paymentType": "SENDER"
            },
            # Ensure 'rateRequestType' is a string value and not an array
            "rateRequestTypes": ["ACCOUNT"],  # Updated this to ensure it is correct
            "requestedPackageLineItems": [
                {
                    "groupPackageCount": 1,
                    "weight": {
                        "units": "LB",
                        "value": trimmed_data.get("packageWeight", 50)
                    },
                    "dimensions": {
                        "length": 20,
                        "width": 20,
                        "height": 20,
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
