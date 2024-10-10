import streamlit as st
import requests

# Streamlit title
st.title("Estes Bearer Token Retriever")

# Retrieve stored secrets
api_key = st.secrets["ESTES_API_KEY"]
username = st.secrets["ESTES_USERNAME"]
password = st.secrets["ESTES_PASSWORD"]

# Display the secrets for verification (comment this out in production for security)
st.write("Using the following credentials:")
st.write(f"API Key: {api_key}")
st.write(f"Username: {username}")
# st.write(f"Password: {password}") # Avoid displaying sensitive information like password

# URL for the Estes authentication endpoint
url = "https://cloudapi.estes-express.com/authenticate"

# Button to trigger token retrieval
if st.button("Get Bearer Token"):
    # Setup headers
    headers = {
        "accept": "application/json",
        "apikey": api_key
    }

    # Send POST request to get the bearer token
    response = requests.post(url, headers=headers, auth=(username, password))

    # Check if the request was successful
    if response.status_code == 200:
        token = response.json().get("access_token", "No token found")
        st.success(f"Bearer Token: {token}")
    else:
        st.error(f"Failed to retrieve token. Status code: {response.status_code}. Message: {response.text}")
