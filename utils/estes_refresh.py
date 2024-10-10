# utils.py

import requests
import os

# Estes API credentials
ESTES_CLIENT_ID = os.getenv("ESTES_CLIENT_ID")  # Your Client ID here
ESTES_CLIENT_SECRET = os.getenv("ESTES_CLIENT_SECRET")  # Your Client Secret here
ESTES_API_KEY = os.getenv("ESTES_API_KEY")  # Your API Key here
ESTES_AUTH_URL = "https://cloudapi.estes-express.com/authenticate"  # Replace with Test or Production URL as needed

def get_bearer_token():
    """
    Retrieves a new bearer token from Estes API using client credentials and API key.
    
    Returns:
        str: The bearer token if the request is successful, else None.
    """
    headers = {
        "accept": "application/json",
        "apikey": ESTES_API_KEY,
    }
    auth = (ESTES_CLIENT_ID, ESTES_CLIENT_SECRET)  # Basic authentication with client ID and secret
    try:
        response = requests.post(ESTES_AUTH_URL, headers=headers, auth=auth)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")  # Extract the token from the response
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception occurred: {e}")
    return None
