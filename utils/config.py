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

# Mapping dictionaries
SALES_REP_MAPPING: Dict[int, str] = {
    7: "Shelley Gummig",
    61802: "Kaitlyn Surry",
    # ... add all your mappings here
}

SHIP_VIA_MAPPING: Dict[int, str] = {
    141: "Our Truck",
    32356: "EPES - Truckload",
    # ... add all your mappings here
}

TERMS_MAPPING: Dict[int, str] = {
    2: "Net 30",
    11: "Credit Card - Prepay",
    # ... add all your mappings here
}