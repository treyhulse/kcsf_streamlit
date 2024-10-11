import streamlit as st
import requests
from utils import estes  # Correctly importing the module from the utils folder

# Render the rate quote request form
st.title("Estes Rate Quote Request")

# Form to collect the rate quote information from the user
with st.form("rate_quote_form"):
    # Ship Date and Ship Time
    ship_date = st.date_input("Ship Date")
    ship_time = st.time_input("Ship Time", value=None)

    # Payment details
    account = st.text_input("Account", value="6100236")
    payor = st.selectbox("Payor", ["Shipper", "Consignee", "Third Party"])
    terms = st.selectbox("Terms", ["Prepaid", "Collect", "Third Party Billing"])

    # Requestor details
    requestor_name = st.text_input("Requestor Name", value="Mary Smith")
    requestor_phone = st.text_input("Requestor Phone", value="8045551234")
    requestor_phone_ext = st.text_input("Requestor Phone Extension", value="123")
    requestor_email = st.text_input("Requestor Email", value="requestor.email@email.com")

    # Origin and Destination details
    origin_name = st.text_input("Origin Name", value="ABC Origin Company")
    origin_address1 = st.text_input("Origin Address 1", value="123 Busy Street")
    origin_city = st.text_input("Origin City", value="Washington")
    origin_state = st.text_input("Origin State/Province", value="DC")
    origin_postal_code = st.text_input("Origin Postal Code", value="20001")
    origin_country = st.text_input("Origin Country", value="US")

    destination_name = st.text_input("Destination Name", value="XYZ Destination Company")
    destination_address1 = st.text_input("Destination Address 1", value="456 Any Street")
    destination_city = st.text_input("Destination City", value="Richmond")
    destination_state = st.text_input("Destination State/Province", value="VA")
    destination_postal_code = st.text_input("Destination Postal Code", value="23234")
    destination_country = st.text_input("Destination Country", value="US")

    # Commodity information
    commodity_weight = st.number_input("Commodity Weight (lbs)", min_value=1, value=500)
    commodity_description = st.text_input("Commodity Description", value="Boxes of widgets")
    is_hazardous = st.checkbox("Hazardous Materials", value=False)

    # Line item details (required by the API)
    line_item_description = st.text_input("Line Item Description", value="Boxes of widgets")
    line_item_weight = st.number_input("Line Item Weight (lbs)", min_value=1, value=commodity_weight)
    line_item_pieces = st.number_input("Line Item Pieces", min_value=1, value=5)
    line_item_classification = st.text_input("Classification", value="92.5")

    # Submit button for form
    submitted = st.form_submit_button("Submit Rate Quote Request")

# Handling the form submission
if submitted:
    # Prepare the rate quote request body based on form input
    rate_quote_body = {
        "quoteRequest": {
            "shipDate": ship_date.strftime("%Y-%m-%d"),
            "shipTime": ship_time.strftime("%H:%M"),
            "serviceLevels": ["LTL", "LTLTC"]
        },
        "payment": {
            "account": account,
            "payor": payor,
            "terms": terms
        },
        "requestor": {
            "name": requestor_name,
            "phone": requestor_phone,
            "phoneExt": requestor_phone_ext,
            "email": requestor_email
        },
        "origin": {
            "name": origin_name,
            "address": {
                "address1": origin_address1,
                "city": origin_city,
                "stateProvince": origin_state,
                "postalCode": origin_postal_code,
                "country": origin_country
            }
        },
        "destination": {
            "name": destination_name,
            "address": {
                "address1": destination_address1,
                "city": destination_city,
                "stateProvince": destination_state,
                "postalCode": destination_postal_code,
                "country": destination_country
            }
        },
        "commodity": {
            "handlingUnits": [
                {
                    "count": 1,
                    "type": "BX",
                    "weight": commodity_weight,
                    "weightUnit": "Pounds",
                    "isHazardous": is_hazardous,
                    "lineItems": [
                        {
                            "description": line_item_description,
                            "weight": line_item_weight,
                            "pieces": line_item_pieces,
                            "classification": line_item_classification
                        }
                    ]
                }
            ]
        }
    }

    # Authenticate and get bearer token
    token = estes.check_and_get_bearer_token()

    # If the token is valid, send the rate quote request
    if token:
        rate_quotes_url = "https://cloudapi.estes-express.com/v1/rate-quotes"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}",
            "apikey": st.secrets["ESTES_API_KEY"]
        }

        # Send the rate quote request
        response = requests.post(rate_quotes_url, headers=headers, json=rate_quote_body)

        # Display the response
        if response.status_code == 200:
            st.success("Rate Quote retrieved successfully.")
            st.json(response.json())  # Display the response JSON
        else:
            st.error(f"Failed to retrieve rate quote. Status code: {response.status_code}. Message: {response.text}")
