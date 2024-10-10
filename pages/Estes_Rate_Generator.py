import streamlit as st
import requests
import base64

# Streamlit UI for displaying title and headers
st.title("Estes Bearer Token Retriever")

# Retrieve stored secrets
api_key = st.secrets["ESTES_API_KEY"]
username = st.secrets["ESTES_USERNAME"]
password = st.secrets["ESTES_PASSWORD"]

# Display the credentials (including the password as requested)
st.write("Using the following credentials:")
st.write(f"API Key: {api_key}")
st.write(f"Username: {username}")
st.write(f"Password: {password}")  # Displaying password for reference

# Encode username and password for the Authorization header
auth_string = f"{username}:{password}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

# URL for the Estes authentication endpoint
url = "https://cloudapi.estes-express.com/authenticate"

# Button to trigger token retrieval
if st.button("Get Bearer Token"):
    # Setup headers
    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {encoded_auth}",  # Using Base64 encoded credentials
        "apikey": api_key
    }

    # Send POST request to get the bearer token
    response = requests.post(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        token = response.json().get("token", "No token found")
        st.success(f"Bearer Token: {token}")
    else:
        st.error(f"Failed to retrieve token. Status code: {response.status_code}. Message: {response.text}")
