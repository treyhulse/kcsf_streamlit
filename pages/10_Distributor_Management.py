import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Distributor Management'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")



################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
import altair as alt
from utils.restlet import fetch_restlet_data

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache_data(ttl=900)
def fetch_raw_data_with_progress(saved_search_id):
    # Initialize progress bar
    progress_bar = st.progress(0)
    
    # Simulating the process in steps (adjust according to your actual fetching time)
    progress_bar.progress(10)  # 10% done
    df = fetch_restlet_data(saved_search_id)
    progress_bar.progress(50)  # 50% done
    
    # Finalize loading
    progress_bar.progress(100)  # 100% done
    progress_bar.empty()  # Remove progress bar when done
    return df

# Fetch raw data for customsearch5135 with progress bar
st.write("Loading data with progress bar...")
customsearch5135_data_raw = fetch_raw_data_with_progress("customsearch5135")

# Check if the data is not empty
if not customsearch5135_data_raw.empty:
    
    # Convert 'Amount' column to numeric if needed
    customsearch5135_data_raw['Amount'] = pd.to_numeric(customsearch5135_data_raw['Amount'], errors='coerce')

    # Aggregate sales via the 'Amount' column by 'Distributor' column
    if 'Distributor' in customsearch5135_data_raw.columns and 'Amount' in customsearch5135_data_raw.columns:
        aggregated_data = customsearch5135_data_raw.groupby('Distributor')['Amount'].sum().reset_index()

        # Format the 'Amount' column to currency format in the aggregated DataFrame for display purposes
        formatted_aggregated_data = aggregated_data.copy()
        formatted_aggregated_data['Amount'] = formatted_aggregated_data['Amount'].apply(lambda x: "${:,.2f}".format(x))

        # Create a layout with columns
        col1, col2 = st.columns([2, 1])

        # Pie chart in the first column (col1)
        with col1:
            st.write("Sales Distribution by Distributor (Pie Chart)")
            pie_chart = alt.Chart(aggregated_data).mark_arc().encode(
                theta=alt.Theta(field="Amount", type="quantitative"),
                color=alt.Color(field="Distributor", type="nominal"),
                tooltip=["Distributor", "Amount"]
            )
            st.altair_chart(pie_chart, use_container_width=True)

        # Aggregated data table in the second column (col2)
        with col2:
            st.write("Aggregated Sales by Distributor:")
            st.dataframe(formatted_aggregated_data)

    else:
        st.error("Required columns 'Distributor' or 'Amount' not found in the data.")
    
    # Place the original DataFrame in an expander at the bottom of the page
    with st.expander("View Raw Data"):
        # Format the 'Amount' column to currency format in the original DataFrame for display purposes
        customsearch5135_data_raw['Amount'] = customsearch5135_data_raw['Amount'].apply(lambda x: "${:,.2f}".format(x))
        st.write("Original Data:")
        st.dataframe(customsearch5135_data_raw)

else:
    st.write("No data available for customsearch5135.")
