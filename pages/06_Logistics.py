import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '01_Shipping Report.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
import pydeck as pdk
from datetime import datetime, timedelta

# Page title
st.title("Logistics Insights")

# Generate more sample order data
data = {
    "Order No.": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    "Ship Date": [
        "2024-08-01", "2024-08-03", "2024-08-05", "2024-08-08", "2024-08-10",
        "2024-08-12", "2024-08-15", "2024-08-18", "2024-08-19", "2024-08-21"
    ],
    "Ship Via": ["FedEx", "UPS", "DHL", "FedEx", "UPS", "FedEx", "UPS", "DHL", "FedEx", "UPS"],
    "lat": [37.7749, 34.0522, 40.7128, 41.8781, 29.7604, 39.7392, 32.7767, 47.6062, 33.4484, 25.7617],
    "lon": [-122.4194, -118.2437, -74.0060, -87.6298, -95.3698, -104.9903, -96.7969, -122.3321, -112.0740, -80.1918],
}

# Create a DataFrame from the sample data
df = pd.DataFrame(data)
df["Ship Date"] = pd.to_datetime(df["Ship Date"])

# Sidebar filters
st.sidebar.header("Filters")

# Order number search
order_filter = st.sidebar.text_input("Search Order No.", "")

# Ship date filter
ship_date_filter = st.sidebar.selectbox("Filter by Ship Date", ["Custom", "Today", "Yesterday", "This Week", "Last Week", "Last 30 Days"])

if ship_date_filter == "Custom":
    start_date = st.sidebar.date_input("Start Date", value=df["Ship Date"].min())
    end_date = st.sidebar.date_input("End Date", value=df["Ship Date"].max())
    date_mask = (df["Ship Date"] >= pd.to_datetime(start_date)) & (df["Ship Date"] <= pd.to_datetime(end_date))
elif ship_date_filter == "Today":
    today = datetime.today().date()
    date_mask = df["Ship Date"].dt.date == today
elif ship_date_filter == "Yesterday":
    yesterday = (datetime.today() - timedelta(days=1)).date()
    date_mask = df["Ship Date"].dt.date == yesterday
elif ship_date_filter == "This Week":
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    date_mask = df["Ship Date"] >= start_of_week
elif ship_date_filter == "Last Week":
    today = datetime.today()
    start_of_last_week = today - timedelta(days=today.weekday() + 7)
    end_of_last_week = today - timedelta(days=today.weekday() + 1)
    date_mask = (df["Ship Date"] >= start_of_last_week) & (df["Ship Date"] <= end_of_last_week)
elif ship_date_filter == "Last 30 Days":
    today = datetime.today()
    last_30_days = today - timedelta(days=30)
    date_mask = df["Ship Date"] >= last_30_days

# Ship via filter
ship_via_filter = st.sidebar.multiselect("Filter by Ship Via", options=df["Ship Via"].unique(), default=df["Ship Via"].unique())

# Apply filters to the data
filtered_df = df[
    (df["Order No."].astype(str).str.contains(order_filter, case=False)) &
    (df["Ship Via"].isin(ship_via_filter)) &
    (date_mask)
]

# Layout with map on the left and table on the right
col1, col2 = st.columns([2, 1])

with col1:
    # Map settings
    selected_order = st.selectbox("Select Order No.", filtered_df["Order No."])

    # Filter map data based on the selected order
    selected_data = filtered_df[filtered_df["Order No."] == selected_order]

    # Display the map with highlighted selection
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=selected_data["lat"].values[0] if not selected_data.empty else df["lat"].mean(),
            longitude=selected_data["lon"].values[0] if not selected_data.empty else df["lon"].mean(),
            zoom=5,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position='[lon, lat]',
                get_color=['[200, 30, 0, 160]' if x == selected_order else '[100, 100, 100, 160]' for x in filtered_df["Order No."]],
                get_radius=50000,
            ),
        ],
    ))

with col2:
    # Display the filtered table
    st.subheader("Orders")
    st.dataframe(filtered_df[["Order No.", "Ship Date", "Ship Via"]])
