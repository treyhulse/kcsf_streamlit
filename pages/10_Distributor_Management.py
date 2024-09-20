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

# Cache the raw data fetching process with a 10-minute expiration
@st.cache_data(ttl=600)
def fetch_raw_data_with_progress(saved_search_id):
    # Initialize progress bar
    progress_bar = st.progress(0)
    
    # Simulating the data loading process in chunks
    df = fetch_restlet_data(saved_search_id)
    progress_bar.progress(33)  # 33% done after fetching data
    
    # Perform initial transformations
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Sales Order'] = df['Sales Order'].astype(str)
    progress_bar.progress(66)  # 66% done after transformation
    
    # Finalize data processing
    df['Date Created'] = pd.to_datetime(df['Date Created'])
    progress_bar.progress(100)  # 100% done
    progress_bar.empty()  # Remove progress bar when done
    return df

# Fetch raw data for customsearch5135 with progress bar
customsearch5135_data_raw = fetch_raw_data_with_progress("customsearch5135")

# Check if the data is not empty
if not customsearch5135_data_raw.empty:
    
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

        # Master line chart aggregating all sales by month, with dots and interactivity
        monthly_sales_data = customsearch5135_data_raw.resample('M', on='Date Created').agg(
            total_sales=('Amount', 'sum')
        ).reset_index()

        st.write("Distributor Program Sales by Month")
        master_line_chart = alt.Chart(monthly_sales_data).mark_line(point=True).encode(
            x=alt.X('Date Created:T', title='Month'),
            y=alt.Y('total_sales:Q', title='Total Sales Amount'),
            tooltip=['Date Created', 'total_sales']
        ).interactive()  # Enable zoom and pan interaction

        st.altair_chart(master_line_chart, use_container_width=True)

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
                st.write("Sales by Distributor:")
                pie_chart = alt.Chart(aggregated_data).mark_arc().encode(
                    theta=alt.Theta(field="total_sales", type="quantitative"),
                    color=alt.Color(field="Distributor", type="nominal"),
                    tooltip=["Distributor", "total_sales"]
                )
                st.altair_chart(pie_chart, use_container_width=True)

            # Aggregated data table in the second column (col2)
            with col2:
                st.write("Sales by Distributor:")
                st.dataframe(formatted_aggregated_data)

            # Stacked bar chart: Group data by Distributor and Quarter
            sales_by_quarter = filtered_data.groupby(['Distributor', 'Quarter']).agg(
                total_sales=('Amount', 'sum')
            ).reset_index()

            st.write("Sales by Distributor by Quarter")
            stacked_bar_chart = alt.Chart(sales_by_quarter).mark_bar().encode(
                x='Distributor',
                y='total_sales',
                color=alt.Color('Quarter', scale=alt.Scale(domain=['Q1', 'Q2', 'Q3', 'Q4'], range=['#FF9999', '#FF6666', '#FF3333', '#FF0000'])),
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
            # Key metrics for the selected distributor
            total_orders = distributor_data['Sales Order'].nunique()
            total_sales = distributor_data['Amount'].sum()
            average_order_volume = distributor_data['Amount'].mean()
            sales_needed = 100000 - total_sales  # Assuming a goal of $100,000 in sales

            # Simulating percentage changes for demonstration purposes
            percentage_change_orders = 5  # Example change for orders
            percentage_change_sales = 2.5  # Example change for sales
            percentage_change_average = -3  # Example change for average order volume
            percentage_change_needed = -15  # Example change for sales needed

            # Display dynamic metric boxes with arrows and sub-numbers
            metrics = [
                {"label": "Total Orders", "value": total_orders, "change": percentage_change_orders, "positive": percentage_change_orders > 0},
                {"label": "Total Sales", "value": f"${total_sales:,.2f}", "change": percentage_change_sales, "positive": percentage_change_sales > 0},
                {"label": "Avg Order Volume", "value": f"${average_order_volume:,.2f}", "change": percentage_change_average, "positive": percentage_change_average > 0},
                {"label": "Sales Needed", "value": f"${sales_needed:,.2f}", "change": percentage_change_needed, "positive": percentage_change_needed > 0},
            ]

            # Styling for the boxes
            st.markdown("""
            <style>
            .metrics-box {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .metric-title {
                margin: 0;
                font-size: 20px;
            }
            .metric-value {
                margin: 0;
                font-size: 28px;
                font-weight: bold;
            }
            .metric-change {
                margin: 0;
                font-size: 14px;
            }
            </style>
            """, unsafe_allow_html=True)

            # First row: metrics
            col1, col2, col3, col4 = st.columns(4)

            for col, metric in zip([col1, col2, col3, col4], metrics):
                arrow = "↑" if metric["positive"] else "↓"
                color = "green" if metric["positive"] else "red"

                with col:
                    st.markdown(f"""
                    <div class="metrics-box">
                        <h3 class="metric-title">{metric['label']}</h3>
                        <p class="metric-value">{metric['value']}</p>
                        <p class="metric-change" style="color:{color};">{arrow} {metric['change']}%</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Add a separation/gap between the two rows
            st.markdown("<hr style='margin-top: 50px; margin-bottom: 50px;'>", unsafe_allow_html=True)

            # Second row: bar chart (left) and dataframe (right)
            left_col, right_col = st.columns(2)

            # Left half: Bar chart showing the distributor's sales across quarters
            with left_col:
                distributor_sales_by_quarter = distributor_data.groupby('Quarter').agg(
                    total_sales=('Amount', 'sum')
                ).reset_index()

                distributor_bar_chart = alt.Chart(distributor_sales_by_quarter).mark_bar().encode(
                    x='Quarter',
                    y='total_sales',
                    color=alt.Color('Quarter', scale=alt.Scale(domain=['Q1', 'Q2', 'Q3', 'Q4'], range=['#FF9999', '#FF6666', '#FF3333', '#FF0000'])),
                    tooltip=['Quarter', 'total_sales']
                ).properties(
                    height=400
                )

                st.altair_chart(distributor_bar_chart, use_container_width=True)

            # Right half: Dataframe for the selected distributor
            with right_col:
                st.subheader(f"Orders for {selected_distributor}")
                st.dataframe(distributor_data)

        else:
            st.write("No data available for the selected distributor.")
