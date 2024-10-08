import streamlit as st
import requests
import base64

# Streamlit UI for displaying title and headers
st.title("Estes Bearer Token and Rate Quotes API")

# Retrieve stored secrets
api_key = st.secrets["ESTES_API_KEY"]
username = st.secrets["ESTES_USERNAME"]
password = st.secrets["ESTES_PASSWORD"]

# Display the credentials for reference (including the password as requested)
st.write("Using the following credentials:")
st.write(f"API Key: {api_key}")
st.write(f"Username: {username}")
st.write(f"Password: {password}")

# Encode username and password for the Authorization header
auth_string = f"{username}:{password}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

# URL for the Estes authentication endpoint
auth_url = "https://cloudapi.estes-express.com/authenticate"

# Function to retrieve the bearer token and store it in session state
def get_bearer_token():
    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {encoded_auth}",
        "apikey": api_key
    }

    response = requests.post(auth_url, headers=headers)

    if response.status_code == 200:
        # Store the bearer token in Streamlit's session state
        st.session_state.bearer_token = response.json().get("token", "No token found")
        st.success("Bearer token successfully retrieved and stored in session state.")
    else:
        st.session_state.bearer_token = None
        st.error(f"Failed to retrieve token. Status code: {response.status_code}. Message: {response.text}")

# Button to trigger token retrieval and storage in session state
if st.button("Get Bearer Token"):
    get_bearer_token()

# Display the bearer token stored in session state if it exists
if "bearer_token" in st.session_state and st.session_state.bearer_token:
    st.write("Bearer Token stored in session state:")
    st.code(st.session_state.bearer_token)
else:
    st.warning("Bearer token not yet retrieved or stored in session state.")

# Add functionality for Rate Quotes API
st.subheader("Rate Quotes API")

# Rate Quotes API URL
rate_quotes_url = "https://cloudapi.estes-express.com/v1/rate-quotes"

# Sample Rate Quotes Request Body
rate_quote_body = {
    "quoteRequest": {
        "shipDate": "2024-11-20",
        "shipTime": "16:00",
        "serviceLevels": ["LTL", "LTLTC"]
    },
    "payment": {
        "account": "6100236",
        "payor": "Shipper",
        "terms": "Prepaid"
    },
    "requestor": {
        "name": "Mary Smith",
        "phone": "8045551234",
        "phoneExt": "123",
        "email": "requestor.email@email.com"
    },
    "fullValueCoverageDetails": {
        "isNeeded": True,
        "monetaryValue": "12500.00"
    },
    "volumeAndExclusiveUseDetails": {
        "linearFootage": 3,
        "distributionCenter": "Food Lion"
    },
    "origin": {
        "name": "ABC Origin Company",
        "locationId": "123",
        "address": {
            "address1": "123 Busy Street",
            "address2": "Suite A",
            "city": "Washington",
            "stateProvince": "DC",
            "postalCode": "20001",
            "country": "US"
        },
        "contact": {
            "name": "Henry Jones",
            "phone": "8045559876",
            "phoneExt": "12",
            "email": "origin.email@email.com"
        }
    },
    "destination": {
        "name": "XYZ Destination Company",
        "locationId": "987-B",
        "address": {
            "address1": "456 Any Street",
            "address2": "Door 2",
            "city": "Richmond",
            "stateProvince": "VA",
            "postalCode": "23234",
            "country": "US"
        },
        "contact": {
            "name": "Lucy Patel",
            "phone": "8045554321",
            "phoneExt": "1212",
            "email": "destination.email@email.com"
        }
    },
    "commodity": {
        "handlingUnits": [
            {
                "count": 1,
                "type": "BX",
                "weight": 500,
                "tareWeight": 10,
                "weightUnit": "Pounds",
                "length": 48,
                "width": 48,
                "height": 48,
                "dimensionsUnit": "Inches",
                "isStackable": True,
                "isTurnable": True,
                "lineItems": [
                    {
                        "description": "Boxes of widgets",
                        "weight": 490,
                        "pieces": 5,
                        "packagingType": "BX",
                        "classification": "92.5",
                        "nmfc": "158880",
                        "nmfcSub": "3",
                        "isHazardous": True,
                        "hazardousDescription": "UN1090, Acetone, 3, PG II",
                        "hazardousDetails": {
                            "weight": 45,
                            "classification": "3",
                            "unnaNumber": 1090,
                            "properName": "Anhydrous ammonia",
                            "technicalName": "NH3",
                            "packagingGroup": "II",
                            "contractNumber": "54321"
                        }
                    }
                ]
            }
        ]
    },
    "accessorials": {
        "codes": ["APT", "ULFEE"]
    }
}

# Button to send rate quote request if the bearer token is available
if st.button("Get Rate Quote"):
    if "bearer_token" in st.session_state and st.session_state.bearer_token:
        # Set up headers for rate quote request
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {st.session_state.bearer_token}",
            "apikey": api_key
        }

        # Send POST request to rate quotes API
        response = requests.post(rate_quotes_url, headers=headers, json=rate_quote_body)

        # Check if the request was successful and display the response
        if response.status_code == 200:
            st.success("Rate Quote retrieved successfully.")

            # Parse response JSON
            data = response.json().get("data", [])

            # Iterate over each quote in the response and build a styled UI container
            for quote in data:
                with st.expander(f"Service Level: {quote['serviceLevelText']} - Quote ID: {quote['quoteId']}"):
                    st.write(f"**Service Level ID:** {quote['serviceLevelId']}")
                    st.write(f"**Quote Expiration:** {quote['dates']['quoteExpiration']}")
                    st.write(f"**Transit Delivery Date:** {quote['dates']['transitDeliveryDate']} @ {quote['dates']['transitDeliveryTime']}")
                    st.write(f"**Total Charges:** ${quote['quoteRate']['totalCharges']}")
                    st.write(f"**Total Shipment Weight:** {quote['quoteRate']['totalShipmentWeight']} lbs")

                    # Display transit details
                    transit_details = quote.get("transitDetails", {})
                    st.write(f"**Transit Days:** {transit_details.get('transitDays', 'N/A')}")
                    st.write(f"**Lane Type:** {transit_details.get('laneType', 'N/A')}")
                    st.write(f"**Origin Terminal:** {transit_details.get('originTerminal', 'N/A')}")
                    st.write(f"**Destination Terminal:** {transit_details.get('destinationTerminal', 'N/A')}")

                    # Display rated accessorials
                    st.write("### Rated Accessorials")
                    for accessorial in quote['quoteRate'].get('ratedAccessorials', []):
                        st.write(f"- **{accessorial['description']}**: ${accessorial['charge']}")

                    # Display line item charges
                    st.write("### Line Item Charges")
                    for line_item in quote.get("lineItemCharges", []):
                        st.write(f"- **{line_item['description']}**: ${line_item['charge']}")

                    # Display additional charge items
                    st.write("### Additional Charges")
                    for charge_item in quote.get("chargeItems", []):
                        st.write(f"- **{charge_item['description']}**: ${charge_item['charge']}")

                    # Disclaimers URL
                    st.write(f"[Disclaimers and Terms]({quote['disclaimersURL']})")

        else:
            st.error(f"Failed to retrieve rate quote. Status code: {response.status_code}. Message: {response.text}")
    else:
        st.warning("Bearer token not found. Please retrieve the bearer token first.")
