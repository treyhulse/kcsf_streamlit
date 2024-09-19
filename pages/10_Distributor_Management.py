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

# Set the title of the page
st.title("Distributor Management")

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
    
    # Convert 'Amount' and 'Sales Order' columns to appropriate types
    customsearch5135_data_raw['Amount'] = pd.to_numeric(customsearch5135_data_raw['Amount'], errors='coerce')
    
    # Ensure 'Sales Order' is treated as a categorical or string column
    customsearch5135_data_raw['Sales Order'] = customsearch5135_data_raw['Sales Order'].astype(str)

    # Convert the 'Date Created' column to datetime
    customsearch5135_data_raw['Date Created'] = pd.to_datetime(customsearch5135_data_raw['Date Created'])
    customsearch5135_data_raw['Date Created'] = pd.to_datetime(customsearch5135_data_raw['Date Created'])

    # Aggregate sales via the 'Amount' column by 'Distributor' column
    if 'Distributor' in customsearch5135_data_raw.columns and 'Amount' in customsearch5135_data_raw.columns:
        aggregated_data = customsearch5135_data_raw.groupby('Distributor').agg(
            total_sales=('Amount', 'sum'),
            unique_sales_orders=('Sales Order', 'nunique')
        ).reset_index()

        # Format the 'total_sales' column to currency format in the aggregated DataFrame for display purposes
        formatted_aggregated_data = aggregated_data.copy()
        formatted_aggregated_data['total_sales'] = formatted_aggregated_data['total_sales'].apply(lambda x: "${:,.2f}".format(x))

        # Create a layout with columns
        col1, col2 = st.columns([2, 1])

        # Pie chart in the first column (col1)
        with col1:
            st.write("Sales Distribution by Distributor (Pie Chart)")
            pie_chart = alt.Chart(aggregated_data).mark_arc().encode(
                theta=alt.Theta(field="total_sales", type="quantitative"),
                color=alt.Color(field="Distributor", type="nominal"),
                tooltip=["Distributor", "total_sales"]
            )
            st.altair_chart(pie_chart, use_container_width=True)

        # Aggregated data table in the second column (col2)
        with col2:
            st.write("Aggregated Sales by Distributor:")
            st.dataframe(formatted_aggregated_data)

        # Stacked bar chart: Group data by Distributor and Quarter
        customsearch5135_data_raw['quarter'] = customsearch5135_data_raw['Date Created'].dt.to_period('Q')

        # Create a stacked bar chart by Distributor and Quarter
        sales_by_quarter = customsearch5135_data_raw.groupby(['Distributor', 'quarter']).agg(
            total_sales=('Amount', 'sum')
        ).reset_index()

        st.write("Sales by Distributor and Quarter (Stacked Bar Chart)")
        stacked_bar_chart = alt.Chart(sales_by_quarter).mark_bar().encode(
            x='Distributor',
            y='total_sales',
            color='quarter',
            tooltip=['Distributor', 'quarter', 'total_sales']
        ).properties(
            height=400
        )

        # Display the stacked bar chart below the pie chart and aggregated dataframe
        st.altair_chart(stacked_bar_chart, use_container_width=True)

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
