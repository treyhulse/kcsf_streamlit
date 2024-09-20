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
    
    # Convert 'Amount' and 'Sales Order' columns to appropriate types
    customsearch5135_data_raw['Amount'] = pd.to_numeric(customsearch5135_data_raw['Amount'], errors='coerce')
    
    # Ensure 'Sales Order' is treated as a categorical or string column
    customsearch5135_data_raw['Sales Order'] = customsearch5135_data_raw['Sales Order'].astype(str)

    # Convert the 'Date Created' column to datetime
    customsearch5135_data_raw['Date Created'] = pd.to_datetime(customsearch5135_data_raw['Date Created'])

    # Define quarter ranges for 2024
    def assign_quarter(date):
        if date >= pd.Timestamp("2024-01-01") and date <= pd.Timestamp("2024-03-31"):
            return 'Q1'
        elif date >= pd.Timestamp("2024-04-01") and date <= pd.Timestamp("2024-06-30"):
            return 'Q2'
        elif date >= pd.Timestamp("2024-07-01") and date <= pd.Timestamp("2024-09-30"):
            return 'Q3'
        else:
            return 'Q4'

    # Apply the quarter assignment based on 'Date Created'
    customsearch5135_data_raw['Quarter'] = customsearch5135_data_raw['Date Created'].apply(assign_quarter)

    # Sidebar filter for Quarter
    selected_quarter = st.sidebar.multiselect(
        "Filter by Quarter (Date Created)",
        options=['Q1', 'Q2', 'Q3', 'Q4'],
        default=['Q1', 'Q2', 'Q3', 'Q4']
    )

    # Filter the DataFrame based on the selected quarter
    filtered_data = customsearch5135_data_raw[customsearch5135_data_raw['Quarter'].isin(selected_quarter)]

    # Create tabs for overall view and specific distributor analysis
    tab1, tab2 = st.tabs(["Distributor Overview", "Distributor Insights"])

    # ---- Tab 1: Distributor Overview ----
    with tab1:
        st.header("Distributor Overview")
        
        # Aggregate sales via the 'Amount' column by 'Distributor' column
        if 'Distributor' in customsearch5135_data_raw.columns and 'Amount' in customsearch5135_data_raw.columns:
            aggregated_data = filtered_data.groupby('Distributor').agg(
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
            sales_by_quarter = filtered_data.groupby(['Distributor', 'Quarter']).agg(
                total_sales=('Amount', 'sum')
            ).reset_index()

            st.write("Sales by Distributor and Quarter (Stacked Bar Chart)")
            stacked_bar_chart = alt.Chart(sales_by_quarter).mark_bar().encode(
                x='Distributor',
                y='total_sales',
                color=alt.Color('Quarter', scale=alt.Scale(domain=['Q1', 'Q2', 'Q3', 'Q4'], range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])),
                tooltip=['Distributor', 'Quarter', 'total_sales']
            ).properties(
                height=400
            )

            # Display the stacked bar chart below the pie chart and aggregated dataframe
            st.altair_chart(stacked_bar_chart, use_container_width=True)

        else:
            st.error("Required columns 'Distributor' or 'Amount' not found in the data.")

    # ---- Tab 2: Distributor Insights ----
    with tab2:
        st.header("Distributor Insights")

        # Dropdown to select a single distributor
        distributor_list = filtered_data['Distributor'].unique().tolist()
        selected_distributor = st.selectbox("Select a Distributor", distributor_list)

        # Filter data for the selected distributor
        distributor_data = filtered_data[filtered_data['Distributor'] == selected_distributor]

        if not distributor_data.empty:
            # Aggregate data for the selected distributor
            distributor_sales_by_quarter = distributor_data.groupby('Quarter').agg(
                total_sales=('Amount', 'sum'),
                unique_sales_orders=('Sales Order', 'nunique')
            ).reset_index()

            # Display sales insights for the selected distributor
            st.write(f"Sales Insights for {selected_distributor}")
            st.dataframe(distributor_sales_by_quarter)

            # Bar chart showing the distributor's sales across quarters
            distributor_bar_chart = alt.Chart(distributor_sales_by_quarter).mark_bar().encode(
                x='Quarter',
                y='total_sales',
                color=alt.Color('Quarter', scale=alt.Scale(domain=['Q1', 'Q2', 'Q3', 'Q4'], range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])),
                tooltip=['Quarter', 'total_sales', 'unique_sales_orders']
            ).properties(
                height=400
            )

            st.altair_chart(distributor_bar_chart, use_container_width=True)

            # Additional insights or stats can be added here for the selected distributor
            st.write(f"Total Sales Orders: {distributor_sales_by_quarter['unique_sales_orders'].sum()}")
            st.write(f"Total Sales Amount: ${distributor_sales_by_quarter['total_sales'].sum():,.2f}")
        else:
            st.write(f"No data available for {selected_distributor}.")

    # Expander for raw data
    with st.expander("View Raw Data"):
        # Format the 'Amount' column to currency format in the original DataFrame for display purposes
        customsearch5135_data_raw['Amount'] = customsearch5135_data_raw['Amount'].apply(lambda x: "${:,.2f}".format(x))
        st.write("Original Data:")
        st.dataframe(customsearch5135_data_raw)

else:
    st.write("No data available for customsearch5135.")
