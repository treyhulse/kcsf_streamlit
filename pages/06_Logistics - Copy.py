import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation
from utils.data_functions import process_netsuite_data_json, process_netsuite_data_csv
import pandas as pd
from datetime import datetime, timedelta

# Set page layout to wide
st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Logistics'
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

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

# Cache the data loaded from NetSuite to improve speed
@st.cache_data
def load_shipping_data():
    df = process_netsuite_data_json(st.secrets["url_open_so"], sales_rep_mapping)
    
    # Check for 'Ship Date' or 'Ship Date (Admin)' column
    possible_ship_date_columns = ['Ship Date', 'Ship Date (Admin)', 'shipdate', 'ship_date']
    ship_date_column = next((col for col in possible_ship_date_columns if col in df.columns), None)
    
    if ship_date_column:
        df[ship_date_column] = pd.to_datetime(df[ship_date_column], errors='coerce').normalize()
    else:
        st.error("Ship Date column not found in the data. Available columns are:")
        st.write(df.columns.tolist())
        st.stop()
    
    # Ensure 'Ship Via' column exists
    if 'Ship Via' not in df.columns:
        st.error("'Ship Via' column not found in the data. Available columns are:")
        st.write(df.columns.tolist())
        st.stop()
    
    return df, ship_date_column

# Group data by 'Ship Date' and 'Ship Via', counting rows instead of summing quantities
def aggregate_data(df, ship_date_column):
    return df.groupby([ship_date_column, 'Ship Via']).size().reset_index(name='order_count')

# Custom date picker for "This Week", "Next Week", "This Month", "Next Month", and custom range
def get_date_range():
    option = st.selectbox(
        "Select Date Range",
        ["Custom Range", "This Week", "Next Week", "This Month", "Next Month"],
        index=3
    )

    today = datetime.today().date()
    if option == "This Week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=4)
    elif option == "Next Week":
        start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
        end_date = start_date + timedelta(days=4)
    elif option == "This Month":
        start_date = today.replace(day=1)
        next_month = (start_date + timedelta(days=32)).replace(day=1)
        end_date = next_month - timedelta(days=1)
    elif option == "Next Month":
        start_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:
        start_date = st.date_input("Start Date", value=today)
        end_date = st.date_input("End Date", value=today + timedelta(days=7))

    return start_date, end_date

# Skip weekends (Saturday and Sunday)
def filter_weekdays(date_range):
    return [date for date in date_range if date.weekday() < 5]

# Main function
def main():
    st.title("Shipping Calendar")

    # Load shipping data
    with st.spinner("Fetching Open Sales Orders..."):
        df, ship_date_column = load_shipping_data()

    if not df.empty:
        df_aggregated = aggregate_data(df, ship_date_column)

        # Get unique 'Ship Via' values for filtering
        all_ship_vias = df_aggregated['Ship Via'].unique().tolist()
        selected_ship_vias = st.multiselect("Select Ship Via", options=['All'] + all_ship_vias, default='Our Truck')

        # Apply 'Ship Via' filter (if 'All' is selected, include all)
        if 'All' not in selected_ship_vias:
            df_aggregated = df_aggregated[df_aggregated['Ship Via'].isin(selected_ship_vias)]

        # Get the date range using custom date picker
        start_date, end_date = get_date_range()

        # Filter data to the selected date range
        filtered_df = df_aggregated[
            (df_aggregated[ship_date_column] >= pd.to_datetime(start_date)) &
            (df_aggregated[ship_date_column] <= pd.to_datetime(end_date))
        ]

        # Create a list of weekdays to display (max 15 days)
        date_range = pd.date_range(start=start_date, end=end_date).normalize()
        date_range = filter_weekdays(date_range)

        if len(date_range) > 15:
            date_range = date_range[:15]

        # Create a 5-column layout for the calendar with improved cards for each day
        for i in range(0, len(date_range), 5):
            cols = st.columns(5)
            for j, date in enumerate(date_range[i:i + 5]):
                with cols[j]:
                    day_data = filtered_df[filtered_df[ship_date_column] == date]

                    # Generate the list of ship vias and their corresponding order counts
                    if not day_data.empty:
                        order_summary = ""
                        for _, row in day_data.iterrows():
                            order_summary += f"{row['Ship Via']}: {row['order_count']} orders<br>"

                    st.markdown(
                        f'''
                        <div style="border: 2px solid #ddd; border-radius: 10px; padding: 20px; background-color: #f9f9f9;
                                    box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align: center; height: auto;">
                            <h3 style="margin-bottom: 10px;">{date.strftime('%Y-%m-%d')}</h3>
                            <p style="font-size: 18px; color: #666;">{order_summary if not day_data.empty else "No shipments"}</p>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    main()
