import streamlit as st
import pandas as pd
from utils.restlet import fetch_restlet_data  # Custom module for fetching data from NetSuite
from utils.fedex import get_fedex_rate_quote  # Custom module for fetching FedEx rate quotes
from requests_oauthlib import OAuth1
import requests
import json
import time

# Set the title for the entire application
st.title("Transportation Management System")

# Create tabs for navigation
tab1, tab2 = st.tabs(["Rate Generator", "Claim Management"])

# Tab 1: Rate Generator
with tab1:
    # Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
    @st.cache_data(ttl=900)
    def fetch_raw_data(saved_search_id):
        # Fetch raw data from RESTlet without filters
        df = fetch_restlet_data(saved_search_id)
        return df

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

        # Bottom row: FedEx Shipping Options
        if 'fedex_response' in st.session_state and st.session_state['fedex_response']:
            fedex_quote = st.session_state['fedex_response']
            st.markdown("### Available Shipping Options")

            rate_options = fedex_quote.get('output', {}).get('rateReplyDetails', [])
            valid_rate_options = [
                option for option in rate_options
                if 'ratedShipmentDetails' in option and len(option['ratedShipmentDetails']) > 0
            ]

            if valid_rate_options:
                sorted_rate_options = sorted(valid_rate_options, key=lambda x: x['ratedShipmentDetails'][0]['totalNetCharge'])

                # Limit to the top options
                top_rate_options = sorted_rate_options[:8]

                st.write(f"Found {len(top_rate_options)} shipping options")

                # Create an empty container to hold the selected option
                selected_shipping_option = None

                # Create a container for the cards and allow selection
                with st.container():
                    for option in top_rate_options:
                        service_type = option.get('serviceType', 'N/A')
                        service_name = get_service_name(service_type)
                        delivery_time = option.get('deliveryTimestamp', 'N/A')
                        net_charge = option['ratedShipmentDetails'][0]['totalNetCharge']
                        currency = option['ratedShipmentDetails'][0].get('currency', 'USD')

                        # Display as a selectable card
                        if st.button(f"{service_name}: ${net_charge} {currency}", key=service_type):
                            selected_shipping_option = {
                                "service_type": service_type,
                                "net_charge": net_charge,
                                "currency": currency,
                                "netsuite_id": get_netsuite_id(service_type)  # Get the internal NetSuite ID for the service
                            }
                            st.session_state['selected_shipping_option'] = selected_shipping_option

                # Display the selected shipping option
                if 'selected_shipping_option' in st.session_state:
                    selected_option = st.session_state['selected_shipping_option']
                    st.markdown(f"### Selected Shipping Option: {get_service_name(selected_option['service_type'])} (${selected_option['net_charge']} {selected_option['currency']})")

                    # Send the selected shipping option back to NetSuite using REST Web Services
                    if st.button("Submit Shipping Option to NetSuite"):
                        # Create the payload using the selected shipping option's NetSuite ID
                        netsuite_payload = {
                            "shippingCost": selected_option['net_charge'],
                            "shipMethod": {
                                "id": selected_option['netsuite_id']  # Use the mapped NetSuite internal ID
                            }
                        }

                        # NetSuite credentials and setup
                        consumer_key = st.secrets["consumer_key"]
                        consumer_secret = st.secrets["consumer_secret"]
                        token = st.secrets["token_key"]
                        token_secret = st.secrets["token_secret"]
                        realm = st.secrets["realm"]

                        # OAuth1 authentication
                        auth = OAuth1(
                            client_key=consumer_key,
                            client_secret=consumer_secret,
                            resource_owner_key=token,
                            resource_owner_secret=token_secret,
                            realm=realm,
                            signature_method='HMAC-SHA256'
                        )

                        # Headers for the request
                        headers = {
                            'Content-Type': 'application/json',
                            'Prefer': 'return-content'
                        }

                        # Replace the existing code block that handles the response from NetSuite after submission:
                        try:
                            # Update the NetSuite Sales Order with the selected shipping details
                            response = update_netsuite_sales_order(selected_id, selected_option['net_charge'], selected_option['netsuite_id'], headers, auth)

                            # Handle 204 status code as a successful response
                            if response.status_code in [200, 204]:  # Consider 204 as a successful response
                                st.success(f"Shipping option '{get_service_name(selected_option['service_type'])}' submitted successfully to NetSuite!")
                            else:
                                st.error(f"Failed to submit shipping option to NetSuite. Status Code: {response.status_code}")
                                st.write("Response Text:", response.text)
                        except Exception as e:
                            st.error(f"Error occurred while updating NetSuite: {str(e)}")

    else:
        st.error("No sales orders available.")


# Tab 2: Claim Management
with tab2:
    # Assume `get_valid_fedex_token` and `get_fedex_bearer_token` are defined in `utils.fedex`
    from utils.fedex import get_valid_fedex_token, get_fedex_bearer_token

    # Set up the page title and description
    st.title("Carrier Claims Management")
    st.write("Submit and track claims with FedEx directly from this interface.")

    # Create a function to handle FedEx claim submission
    def create_fedex_claim(shipment_tracking_number, claim_type, claim_amount, reason_for_claim, contact_name, contact_phone, contact_email):
        """
        Submits a claim to FedEx for a specified shipment.

        Args:
        - shipment_tracking_number: str, the tracking number of the shipment.
        - claim_type: str, type of claim (e.g., "DAMAGE", "LOSS", "SHORTAGE").
        - claim_amount: float, the amount claimed.
        - reason_for_claim: str, description of the reason for the claim.
        - contact_name: str, the name of the contact person for this claim.
        - contact_phone: str, the phone number of the contact person.
        - contact_email: str, the email address of the contact person.

        Returns:
        - dict, the response from the FedEx API.
        """
        # Get a valid token using the centralized function
        fedex_token = get_valid_fedex_token()

        # Set up the API endpoint and headers
        fedex_claims_url = "https://apis.fedex.com/claims/v1/claims"  # Replace with the correct FedEx endpoint if needed
        headers = {
            "Authorization": f"Bearer {fedex_token}",
            "Content-Type": "application/json"
        }

        # Create the payload for claim submission
        payload = {
            "shipments": [
                {
                    "trackingNumber": shipment_tracking_number,
                    "claimDetails": {
                        "claimType": claim_type,  # Possible values: DAMAGE, LOSS, SHORTAGE
                        "claimAmount": {
                            "value": claim_amount,
                            "currency": "USD"
                        },
                        "reasonForClaim": reason_for_claim,
                        "contact": {
                            "contactName": contact_name,
                            "contactPhoneNumber": contact_phone,
                            "contactEmailAddress": contact_email
                        }
                    }
                }
            ]
        }

        # Make the POST request to FedEx to submit the claim
        response = requests.post(fedex_claims_url, headers=headers, json=payload)

        # Check the response status code
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            st.error(f"Failed to submit claim: {response.status_code} - {response.text}")
            return {"error": f"Failed to submit claim: {response.status_code} - {response.text}"}

    # UI for the claim submission form
    st.subheader("Submit a Claim")

    with st.form("claim_form"):
        # Input fields to collect claim details
        shipment_tracking_number = st.text_input("Shipment Tracking Number", placeholder="Enter the tracking number")
        claim_type = st.selectbox("Claim Type", ["DAMAGE", "LOSS", "SHORTAGE"], help="Select the type of claim")
        claim_amount = st.number_input("Claim Amount (USD)", min_value=0.01, help="Enter the amount you are claiming for this shipment")
        reason_for_claim = st.text_area("Reason for Claim", help="Provide a reason for the claim")

        # Contact details fields
        st.write("Contact Information")
        contact_name = st.text_input("Contact Name", placeholder="Enter contact name for this claim")
        contact_phone = st.text_input("Contact Phone", placeholder="Enter contact phone number")
        contact_email = st.text_input("Contact Email", placeholder="Enter contact email address")

        # Submit button for the form
        submitted = st.form_submit_button("Submit Claim")

        if submitted:
            # Submit the claim to FedEx using the function defined above
            claim_response = create_fedex_claim(shipment_tracking_number, claim_type, claim_amount, reason_for_claim, contact_name, contact_phone, contact_email)

            # Display the response from FedEx
            if "error" not in claim_response:
                st.success("Claim submitted successfully!")
                st.write("Claim Response:", claim_response)
            else:
                st.error("Failed to submit the claim. Please check the details and try again.")

    # Additional section to track an existing claim
    st.subheader("Track an Existing Claim")

    # Input field for claim tracking
    claim_tracking_number = st.text_input("Claim Tracking Number", placeholder="Enter your claim tracking number to check status")

    # Button to track the claim status
    if st.button("Track Claim Status"):
        fedex_token = get_valid_fedex_token()

        # Set up the API endpoint for tracking and headers
        fedex_claims_tracking_url = f"https://apis.fedex.com/claims/v1/claims/{claim_tracking_number}"  # Replace with the correct endpoint if needed
        headers = {
            "Authorization": f"Bearer {fedex_token}",
            "Content-Type": "application/json"
        }

        # Make the GET request to track the claim status
        response = requests.get(fedex_claims_tracking_url, headers=headers)

        if response.status_code == 200:
            claim_status_response = response.json()
            st.write("Claim Status:", claim_status_response)
        else:
            st.error(f"Failed to retrieve claim status: {response.status_code} - {response.text}")
