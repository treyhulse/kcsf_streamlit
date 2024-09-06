import streamlit as st
from typing import Dict

def get_netsuite_config() -> Dict[str, str]:
    return {
        "consumer_key": st.secrets["consumer_key"],
        "consumer_secret": st.secrets["consumer_secret"],
        "token_key": st.secrets["token_key"],
        "token_secret": st.secrets["token_secret"],
        "realm": st.secrets["realm"]
    }

API_URLS = {
    "open_so": st.secrets["url_open_so"]
}

SALES_REP_MAPPING: Dict[int, str] = {
    # Your sales rep mapping here
}

SHIP_VIA_MAPPING: Dict[int, str] = {
    # Your ship via mapping here
}

TERMS_MAPPING: Dict[int, str] = {
    # Your terms mapping here
}