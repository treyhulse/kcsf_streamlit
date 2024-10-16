import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(page_title="Estes Rate Generator", 
                   layout="wide",)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import requests
from utils import estes  # Importing the module from the utils folder

# Define the function to render the quote response before it is used
def render_quote_response(data):
    for quote in data:
        with st.expander(f"Service Level: {quote['serviceLevelText']} - Quote ID: {quote['quoteId']}"):
            st.write(f"**Service Level ID**: {quote['serviceLevelId']}")
            st.write(f"**Rate Found**: {'Yes' if quote['rateFound'] else 'No'}")
            st.write(f"**Quote Expiration**: {quote['dates']['quoteExpiration']}")
            st.write(f"**Transit Delivery Date**: {quote['dates']['transitDeliveryDate']} @ {quote['dates']['transitDeliveryTime']}")
            st.write(f"**Transit Days**: {quote['transitDetails']['transitDays']}")
            st.write(f"**Total Charges**: ${quote['quoteRate']['totalCharges']}")
            st.write(f"**Total Shipment Weight**: {quote['quoteRate']['totalShipmentWeight']} lbs")
            st.write(f"**Rated Linear Feet**: {quote['quoteRate']['ratedLinearFeet']}")

            # Rated Accessorials
            st.subheader("Rated Accessorials")
            for accessorial in quote['quoteRate']['ratedAccessorials']:
                st.write(f"- {accessorial['description']}: ${accessorial['charge']}")

            # Line Item Charges
            st.subheader("Line Item Charges")
            for item in quote['lineItemCharges']:
                st.write(f"- {item['description']}: {item['weight']} lbs, Charge: ${item['charge']}")

            # Total Charge Items
            st.subheader("Total Charge Items")
            for charge_item in quote['chargeItems']:
                st.write(f"- {charge_item['description']}: ${charge_item['charge']}")

            # Alerts
            if quote.get("alerts"):
                st.warning("Alerts:")
                for alert in quote['alerts']:
                    st.write(f"- {alert['message']}")

            # Disclaimers
            st.write(f"[Disclaimers and Terms]({quote['disclaimersURL']})")

# Render the rate quote request form
st.title("Estes Rate Quote Request")

# Define columns for layout
col1, col2 = st.columns(2)

# Open the form context
with st.form(key="rate_quote_form"):
    with col1:
        st.header("Shipment Information")

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

# Handling the form submission and display response (col2 - right)
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

    # Display the response in col2 (right column)
    with col2:
        st.title("Estes Rate Quote Response")

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
                response_data = response.json()
                if response_data['error']['code'] == 0:
                    st.success("Rate Quote retrieved successfully!")
                    render_quote_response(response_data['data'])  # Call function to render response
                else:
                    st.error(f"Failed to retrieve rate quote. Message: {response_data['error']['message']}")
            else:
                st.error(f"Failed to retrieve rate quote. Status code: {response.status_code}. Message: {response.text}")

    token = estes.check_and_get_bearer_token()
