import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.data_functions import process_netsuite_data_csv, replace_ids_with_display_values
from utils.connections import connect_to_netsuite
from utils.mappings import sales_rep_mapping, ship_via_mapping, terms_mapping

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"You have access to this page.")

def main():
    st.header("Open Sales Orders Analysis")
    
    try:
        # Connect to NetSuite
        netsuite_base_url, headers = connect_to_netsuite()
        
        # Construct the full URL for the open sales orders restlet
        url_open_so = f"{netsuite_base_url}{st.secrets['url_open_so']}"
        
        with st.spinner("Fetching Open Sales Orders..."):
            df_open_so = process_netsuite_data_csv(url_open_so)
        
        if not df_open_so.empty:
            st.success("Data loaded successfully!")
            
            # Apply mappings
            df_open_so = replace_ids_with_display_values(df_open_so, sales_rep_mapping)
            if 'shipvia' in df_open_so.columns:
                df_open_so['shipvia'] = df_open_so['shipvia'].replace(ship_via_mapping)
            if 'terms' in df_open_so.columns:
                df_open_so['terms'] = df_open_so['terms'].replace(terms_mapping)
            
            # Display column names for debugging
            st.write("Available columns:", df_open_so.columns.tolist())
            
            # Display the dataframe
            st.write("Open Sales Orders Data:")
            st.dataframe(df_open_so)
            
            # Provide download option
            csv = df_open_so.to_csv(index=False)
            st.download_button(label="Download data as CSV", 
                               data=csv, 
                               file_name="open_sales_orders.csv", 
                               mime="text/csv")
        else:
            st.warning("No data retrieved from the restlet.")
    
    except Exception as e:
        st.error(f"Failed to fetch or process data: {str(e)}")

if __name__ == "__main__":
    main()