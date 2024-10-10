import streamlit as st
import requests
import base64

# Streamlit UI for displaying title and headers
st.title("Estes Bearer Token Retriever")

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
url = "https://cloudapi.estes-express.com/authenticate"

# Function to retrieve the bearer token and store it in session state
def get_bearer_token():
    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {encoded_auth}",
        "apikey": api_key
    }

    response = requests.post(url, headers=headers)

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
