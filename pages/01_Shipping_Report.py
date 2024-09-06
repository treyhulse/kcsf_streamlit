import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Shipping Report'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################
import pandas as pd
import plotly.express as px
from utils.data_functions import process_netsuite_data_csv, fetch_all_data_csv
from datetime import date, timedelta
import requests
from io import StringIO


# Sales Rep mapping
sales_rep_mapping = {
    7: "Shelley Gummig",
    61802: "Kaitlyn Surry",
    4125270: "Becky Dean",
    4125868: "Roger Dixon",
    4131659: "Lori McKiney",
    47556: "Raymond Brown",
    4169685: "Shellie Pritchett",
    4123869: "Katelyn Kennedy",
    47708: "Phil Vaughan",
    4169200: "Dave Knudtson",
    4168032: "Trey Hulse",
    4152972: "Gary Bargen",
    4159935: "Derrick Lewis",
    66736: "Unspecified",
    67473: 'Jon Joslin',
}

# Ship Via mapping
ship_via_mapping = {
    141: "Our Truck",
    32356: "EPES - Truckload",
    226: "Pickup 2",
    36191: "Estes Standard",
    36: "Fed Ex Ground",
    3653: "Fed Ex Ground Home Delivery",
    7038: "Other - See Shipping Info",
    4: "UPS Ground",
    227: "Dayton Freight"
}

# Terms mapping
terms_mapping = {
    2: "Net 30",
    11: "Credit Card - Prepay",
    10: "Prepay",
    13: "Net 45",
    3: "Net 60",
    19: "Check",
    27: "ACH",
    37: "Account Credit",
    18: "No Charge"
}

st.markdown(
    """
    <style>
    .metric-box {
        background-color: var(--primary-background-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def create_ship_date_chart(df):
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    ship_date_counts = df['Ship Date'].value_counts().sort_index()
    fig = px.line(
        x=ship_date_counts.index,
        y=ship_date_counts.values,
        labels={'x': 'Ship Date', 'y': 'Number of Orders'},
        title='Open Sales Orders by Ship Date'
    )
    fig.update_layout(
        xaxis_title='Ship Date',
        yaxis_title='Number of Orders',
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

def create_pie_chart(matched_orders, unmatched_orders):
    pie_data = pd.DataFrame({
        'Task Status': ['Tasked Orders', 'Untasked Orders'],
        'Count': [matched_orders, unmatched_orders]
    })
    fig = px.pie(
        pie_data,
        names='Task Status',
        values='Count',
        title='Tasked vs Untasked Orders',
        hole=0.4
    )
    fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))
    return fig

def get_date_range(preset):
    today = date.today()
    if preset == "Today":
        return today, today
    elif preset == "Tomorrow":
        return today + timedelta(days=1), today + timedelta(days=1)
    elif preset == "This Week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week
    elif preset == "This Month":
        start_of_month = today.replace(day=1)
        next_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_of_month = next_month - timedelta(days=1)
        return start_of_month, end_of_month
    else:
        return None, None

def main():
    # Step 1: Fetch the data from the RESTlet
    with st.spinner("Fetching Open Sales Orders..."):
        csv_data = fetch_all_data_csv(st.secrets["url_open_so"])  # Fetch the CSV data from the RESTlet

    # Step 2: Convert the CSV data into a DataFrame
    df_open_so = pd.read_csv(StringIO(csv_data))

    # Step 3: Display the DataFrame
    st.write(df_open_so)

    # Continue with filtering, analysis, and visualization
    # For example, applying filters to "Ship Via" column
    st.sidebar.subheader("Filter by Ship Via")
    ship_vias = ['All'] + sorted(df_open_so['Ship Via'].unique())
    selected_ship_vias = st.sidebar.multiselect("Select Ship Via", ship_vias, default=['All'])

    # Filter the DataFrame based on the selected Ship Via
    if 'All' not in selected_ship_vias:
        df_open_so = df_open_so[df_open_so['Ship Via'].isin(selected_ship_vias)]

    # Display the filtered data
    st.dataframe(df_open_so)

    # Example: Create a visualization (Ship Date Line Chart)
    st.subheader("Ship Date Line Chart")
    df_open_so['Ship Date'] = pd.to_datetime(df_open_so['Ship Date'])
    ship_date_counts = df_open_so['Ship Date'].value_counts().sort_index()
    st.line_chart(ship_date_counts)

# Utility function to fetch all data from RESTlet as CSV
def fetch_all_data_csv(url):
    """Fetch all data from the RESTlet as CSV."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.content.decode('utf-8')  # Return the CSV as a string
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return ""

# Run the main function
if __name__ == "__main__":
    main()