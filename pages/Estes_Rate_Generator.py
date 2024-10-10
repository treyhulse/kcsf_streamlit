import streamlit as st
from utils.estes import get_freight_quote, refresh_token

# Streamlit page configuration
st.set_page_config(page_title="Estes LTL Shipment Rate Generator", page_icon="🚚", layout="wide")

# Page title
st.title("Estes LTL Shipment Rate Generator")

# Refresh Bearer Token Button
if st.button("Refresh Bearer Token"):
    refresh_token()

# Collapsible section for Requestor Details
with st.expander("Requestor Details"):
    requestor_name = st.text_input("Requestor Name", value="Mary Smith")
    requestor_phone = st.text_input("Requestor Phone", value="8045551234")
    requestor_phone_ext = st.text_input("Requestor Phone Extension", value="123")
    requestor_email = st.text_input("Requestor Email", value="requestor.email@email.com")

# Collapsible section for Payment Details
with st.expander("Payment Details"):
    payment_account = st.text_input("Account Number", value="6100236")  # Pre-filled for testing
    payment_payor = st.selectbox("Payor", ["Shipper", "Consignee", "Third Party"], index=0)
    payment_terms = st.selectbox("Terms", ["Prepaid", "Collect"], index=0)

# Collapsible section for Shipment Details
with st.expander("Shipment Details"):
    ship_date = st.date_input("Ship Date", value=pd.to_datetime("2024-11-20"))  # Ship date as per request
    ship_time = st.text_input("Ship Time", value="16:00")
    service_levels = st.multiselect("Service Levels", ["LTL", "LTLTC", "Volume LTL"], default=["LTL", "LTLTC"])

# Collapsible section for Origin and Destination
with st.expander("Origin and Destination"):
    origin_name = st.text_input("Origin Company Name", value="ABC Origin Company")
    origin_address1 = st.text_input("Origin Address 1", value="123 Busy Street")
    origin_address2 = st.text_input("Origin Address 2", value="Suite A")
    origin_city = st.text_input("Origin City", value="Washington")
    origin_state = st.text_input("Origin State/Province", value="DC")
    origin_postal_code = st.text_input("Origin Postal Code", value="20001")
    origin_country = st.selectbox("Origin Country", ["US", "MX", "CA"], index=0)
    origin_contact_name = st.text_input("Origin Contact Name", value="Henry Jones")
    origin_contact_phone = st.text_input("Origin Contact Phone", value="8045559876")
    origin_contact_phone_ext = st.text_input("Origin Contact Phone Extension", value="12")
    origin_contact_email = st.text_input("Origin Contact Email", value="origin.email@email.com")

    destination_name = st.text_input("Destination Company Name", value="XYZ Destination Company")
    destination_address1 = st.text_input("Destination Address 1", value="456 Any Street")
    destination_address2 = st.text_input("Destination Address 2", value="Door 2")
    destination_city = st.text_input("Destination City", value="Richmond")
    destination_state = st.text_input("Destination State/Province", value="VA")
    destination_postal_code = st.text_input("Destination Postal Code", value="23234")
    destination_country = st.selectbox("Destination Country", ["US", "MX", "CA"], index=0)
    destination_contact_name = st.text_input("Destination Contact Name", value="Lucy Patel")
    destination_contact_phone = st.text_input("Destination Contact Phone", value="8045554321")
    destination_contact_phone_ext = st.text_input("Destination Contact Phone Extension", value="1212")
    destination_contact_email = st.text_input("Destination Contact Email", value="destination.email@email.com")

# Collapsible section for Commodity Details
with st.expander("Commodity Details"):
    handling_unit_count = st.number_input("Handling Unit Count", value=1, min_value=1)
    handling_unit_type = st.selectbox("Handling Unit Type", ["BX", "PLT", "DRM"], index=0)
    weight = st.number_input("Weight (lbs)", value=500, min_value=1)
    length = st.number_input("Length (inches)", value=48, min_value=1)
    width = st.number_input("Width (inches)", value=48, min_value=1)
    height = st.number_input("Height (inches)", value=48, min_value=1)
    is_stackable = st.checkbox("Is Stackable?", value=True)
    is_turnable = st.checkbox("Is Turnable?", value=True)

# Full Value Coverage and Additional Details
with st.expander("Full Value Coverage and Additional Details"):
    is_coverage_needed = st.checkbox("Is Full Value Coverage Needed?", value=True)
    monetary_value = st.text_input("Monetary Value", value="12500.00")
    linear_footage = st.number_input("Linear Footage", value=3, min_value=1)
    distribution_center = st.text_input("Distribution Center", value="Food Lion")
    accessorials_codes = st.multiselect("Accessorial Codes", ["APT", "ULFEE", "RAMP", "DHFEE"], default=["APT", "ULFEE"])

# Button to submit the freight quote request
if st.button("Get Freight Quote"):
    # Build the JSON request body based on input fields
    request_body = {
        "quoteRequest": {
            "shipDate": str(ship_date),
            "shipTime": ship_time,
            "serviceLevels": service_levels
        },
        "payment": {
            "account": payment_account,
            "payor": payment_payor,
            "terms": payment_terms
        },
        "requestor": {
            "name": requestor_name,
            "phone": requestor_phone,
            "phoneExt": requestor_phone_ext,
            "email": requestor_email
        },
        "fullValueCoverageDetails": {
            "isNeeded": is_coverage_needed,
            "monetaryValue": monetary_value
        },
        "volumeAndExclusiveUseDetails": {
            "linearFootage": linear_footage,
            "distributionCenter": distribution_center
        },
        "origin": {
            "name": origin_name,
            "locationId": "123",  # Assuming a static location ID for now
            "address": {
                "address1": origin_address1,
                "address2": origin_address2,
                "city": origin_city,
                "stateProvince": origin_state,
                "postalCode": origin_postal_code,
                "country": origin_country
            },
            "contact": {
                "name": origin_contact_name,
                "phone": origin_contact_phone,
                "phoneExt": origin_contact_phone_ext,
                "email": origin_contact_email
            }
        },
        "destination": {
            "name": destination_name,
            "locationId": "987-B",  # Assuming a static location ID for now
            "address": {
                "address1": destination_address1,
                "address2": destination_address2,
                "city": destination_city,
                "stateProvince": destination_state,
                "postalCode": destination_postal_code,
                "country": destination_country
            },
            "contact": {
                "name": destination_contact_name,
                "phone": destination_contact_phone,
                "phoneExt": destination_contact_phone_ext,
                "email": destination_contact_email
            }
        },
        "commodity": {
            "handlingUnits": [
                {
                    "count": handling_unit_count,
                    "type": handling_unit_type,
                    "weight": weight,
                    "weightUnit": "Pounds",
                    "length": length,
                    "width": width,
                    "height": height,
                    "dimensionsUnit": "Inches",
                    "isStackable": is_stackable,
                    "isTurnable": is_turnable,
                    "lineItems": []  # Placeholder for any additional line items
                }
            ]
        },
        "accessorials": {
            "codes": accessorials_codes
        }
    }

    # Send the freight quote request
    quote = get_freight_quote(
        pickup_zip=origin_postal_code,
        delivery_zip=destination_postal_code,
        weight=weight,
        handling_units=handling_unit_count
    )

    # Display the response
    if quote:
        st.subheader("Freight Quote Details")
        st.json(quote)
    else:
        st.warning("Failed to retrieve a freight quote. Check input values and try again.")
