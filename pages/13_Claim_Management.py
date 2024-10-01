import streamlit as st
import requests
import time

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
