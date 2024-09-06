import streamlit as st
import pandas as pd
import requests
from requests_oauthlib import OAuth1
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_netsuite_auth():
    return OAuth1(
        st.secrets["consumer_key"],
        st.secrets["consumer_secret"],
        st.secrets["token_key"],
        st.secrets["token_secret"],
        realm=st.secrets["realm"],
        signature_method='HMAC-SHA256'
    )

def fetch_data(url: str, page: int = 1) -> Dict[str, Any]:
    """Fetch data from a NetSuite RESTlet endpoint."""
    auth = get_netsuite_auth()
    full_url = f"{url}&page={page}"
    logger.info(f"Fetching data from URL: {full_url}")
    response = requests.get(full_url, auth=auth)
    response.raise_for_status()
    return response.json()

def process_netsuite_data(url: str) -> pd.DataFrame:
    """Fetch and process NetSuite data."""
    all_data = []
    page = 1
    while True:
        try:
            data = fetch_data(url, page)
            if 'results' not in data or not data['results']:
                logger.warning(f"No results found on page {page}")
                break
            all_data.extend(data['results'])
            if not data.get('hasMore', False):
                break
            page += 1
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data on page {page}: {str(e)}")
            break
    
    if not all_data:
        logger.error("No data retrieved from NetSuite")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    logger.info(f"Retrieved {len(df)} records from NetSuite")
    return df

def main():
    st.title("NetSuite Open Sales Orders")

    try:
        with st.spinner("Fetching data from NetSuite..."):
            df = process_netsuite_data(st.secrets["url_open_so"])
        
        if not df.empty:
            st.success(f"Data fetched successfully! Retrieved {len(df)} records.")
            
            # Display summary metrics
            st.subheader("Summary Metrics")
            total_orders = len(df)
            total_amount = df['Amount Remaining'].sum() if 'Amount Remaining' in df.columns else 0
            unique_customers = df['Name'].nunique() if 'Name' in df.columns else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Orders", total_orders)
            col2.metric("Total Amount Remaining", f"${total_amount:,.2f}")
            col3.metric("Unique Customers", unique_customers)
            
            # Display data table
            st.subheader("Open Sales Orders")
            st.dataframe(df)
            
            # Display chart of orders by ship date if 'Ship Date' column exists
            if 'Ship Date' in df.columns:
                st.subheader("Orders by Ship Date")
                df['Ship Date'] = pd.to_datetime(df['Ship Date'])
                orders_by_date = df.groupby('Ship Date').size().reset_index(name='Count')
                st.line_chart(orders_by_date.set_index('Ship Date'))
            
            # Allow CSV download of processed data
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="netsuite_sales_orders.csv",
                mime="text/csv",
            )
        else:
            st.warning("No data retrieved from NetSuite.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.exception("Error in main function")

if __name__ == "__main__":
    main()