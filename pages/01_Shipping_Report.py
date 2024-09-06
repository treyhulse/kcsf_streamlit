import streamlit as st
import pandas as pd
import requests
from requests_oauthlib import OAuth1

def get_netsuite_auth():
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

def fetch_netsuite_data():
    auth = get_netsuite_auth()
    response = requests.get(st.secrets["url_open_so"], auth=auth)
    response.raise_for_status()
    return response.json()

def main():
    st.title("NetSuite Data Display")

    try:
        with st.spinner("Fetching data from NetSuite..."):
            data = fetch_netsuite_data()
        
        if data:
            df = pd.DataFrame(data)
            st.success("Data fetched successfully!")
            st.dataframe(df)
        else:
            st.warning("No data retrieved from NetSuite.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()