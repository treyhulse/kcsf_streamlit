import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from utils.data_functions import process_netsuite_data_json
from requests.exceptions import RequestException
from datetime import datetime, timedelta
import logging

# Set page config
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Title
st.title("Sales Dashboard")

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

# State lat/lon dictionary for mapping
state_lat_lon = {
    'AL': [32.806671, -86.791130],
    'AK': [61.370716, -152.404419],
    'AZ': [33.729759, -111.431221],
    'AR': [34.969704, -92.373123],
    'CA': [36.116203, -119.681564],
    'CO': [39.059811, -105.311104],
    'CT': [41.597782, -72.755371],
    'DE': [39.318523, -75.507141],
    'FL': [27.766279, -81.686783],
    'GA': [33.040619, -83.643074],
    'HI': [21.094318, -157.498337],
    'ID': [44.240459, -114.478828],
    'IL': [40.349457, -88.986137],
    'IN': [39.849426, -86.258278],
    'IA': [42.011539, -93.210526],
    'KS': [38.526600, -96.726486],
    'KY': [37.668140, -84.670067],
    'LA': [31.169546, -91.867805],
    'ME': [44.693947, -69.381927],
    'MD': [39.063946, -76.802101],
    'MA': [42.230171, -71.530106],
    'MI': [43.326618, -84.536095],
    'MN': [45.694454, -93.900192],
    'MS': [32.741646, -89.678696],
    'MO': [38.456085, -92.288368],
    'MT': [46.921925, -110.454353],
    'NE': [41.125370, -98.268082],
    'NV': [38.313515, -117.055374],
    'NH': [43.452492, -71.563896],
    'NJ': [40.298904, -74.521011],
    'NM': [34.840515, -106.248482],
    'NY': [42.165726, -74.948051],
    'NC': [35.630066, -79.806419],
    'ND': [47.528912, -99.784012],
    'OH': [40.388783, -82.764915],
    'OK': [35.565342, -96.928917],
    'OR': [44.572021, -122.070938],
    'PA': [40.590752, -77.209755],
    'RI': [41.680893, -71.511780],
    'SC': [33.856892, -80.945007],
    'SD': [44.299782, -99.438828],
    'TN': [35.747845, -86.692345],
    'TX': [31.054487, -97.563461],
    'UT': [40.150032, -111.862434],
    'VT': [44.045876, -72.710686],
    'VA': [37.769337, -78.169968],
    'WA': [47.400902, -121.490494],
    'WV': [38.491226, -80.954456],
    'WI': [44.268543, -89.616508],
    'WY': [42.755966, -107.302490],
    'BC': [53.7267, -127.6476],  # British Columbia
    'ON': [51.2538, -85.3232],   # Ontario
}

@st.cache_data
def fetch_data(url, mapping, retries=3, delay=5):
    """Fetch data from the NetSuite RESTlet API."""
    attempt = 0
    while attempt < retries:
        try:
            df_sales = process_netsuite_data_json(url, mapping)
            if df_sales.empty:
                st.warning("No data returned from the API. Please check your API and data source.")
                return pd.DataFrame()
            df_sales['trandate'] = pd.to_datetime(df_sales['trandate'])
            
            # Apply the sales rep mapping
            df_sales['salesrep'] = pd.to_numeric(df_sales['salesrep'], errors='coerce', downcast='integer')
            df_sales['salesrep'] = df_sales['salesrep'].map(mapping).fillna(df_sales['salesrep'])

            return df_sales
        except RequestException as e:
            attempt += 1
            st.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    st.error(f"Failed to fetch data after {retries} attempts.")
    return pd.DataFrame()

# Fetch data from API
logger.info("Fetching data from the API...")
df_sales = fetch_data(st.secrets["url_sales"], sales_rep_mapping)
if df_sales.empty:
    st.warning("No data fetched. Please check the API or data source.")
    st.stop()

logger.info("Data fetched successfully")

# Filter to include only fully billed orders
df_sales = df_sales[df_sales['statusref'] == 'fullyBilled']

# Ensure 'amount' is numeric
df_sales['amount'] = pd.to_numeric(df_sales['amount'], errors='coerce')

# Sidebar filters
st.sidebar.header("Filters")

# Date filter shortcuts
date_filter = st.sidebar.selectbox("Select Date Filter", ["Today", "This Week", "This Month", "This Quarter", "This Year"])

# Calculate date ranges for filtering
if date_filter == "Today":
    start_date = datetime.now().date()
elif date_filter == "This Week":
    start_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
elif date_filter == "This Month":
    start_date = datetime.now().replace(day=1)
elif date_filter == "This Quarter":
    month = (datetime.now().month - 1) // 3 * 3 + 1
    start_date = datetime.now().replace(month=month, day=1)
elif date_filter == "This Year":
    start_date = datetime.now().replace(month=1, day=1)

logger.info(f"Filtering data based on date: {date_filter}")
df_sales = df_sales[df_sales['trandate'] >= pd.to_datetime(start_date)]

# Sales Rep filter
sales_reps = df_sales['salesrep'].unique().tolist()
selected_sales_reps = st.sidebar.multiselect("Filter by Sales Rep", sales_reps, default=sales_reps)

# Apply sales rep filter
df_sales = df_sales[df_sales['salesrep'].isin(selected_sales_reps)]

# Map Visualization by State
st.subheader("Sales by State")

# Group by state and sum the 'amount'
state_sales = df_sales.groupby('shipstate')['amount'].sum().reset_index()

# Remove rows where 'shipstate' is NaN
state_sales = state_sales.dropna(subset=['shipstate'])

logger.info(f"Mapping lat/lon based on shipstate")
# Merge lat/lon into state_sales DataFrame from the state_lat_lon dictionary
state_sales['lat'] = state_sales['shipstate'].map(lambda x: state_lat_lon.get(x, [0, 0])[0])
state_sales['lon'] = state_sales['shipstate'].map(lambda x: state_lat_lon.get(x, [0, 0])[1])

# Ensure data types are correct for PyDeck
state_sales = state_sales.astype({'lat': 'float64', 'lon': 'float64', 'amount': 'float64'})

# Display the cleaned state_sales DataFrame alongside the map for verification
st.dataframe(state_sales)

# Verify that state_sales contains valid data for mapping
if state_sales.empty:
    st.warning("No data available for map visualization.")
else:
    # Create PyDeck map layer with increased circle size
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=state_sales,
        get_position='[lon, lat]',
        get_radius='amount / .1',  # Increased circle size by reducing the divisor (was 100, now 10)
        get_color='[200, 30, 0, 160]',
        pickable=True,
    )

    # Define PyDeck view
    view_state = pdk.ViewState(latitude=37.7749, longitude=-95.7129, zoom=3)

    # Render map
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    logger.info("Map rendered successfully with larger circles")


# Metrics Section
st.subheader("Key Sales Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"${state_sales['amount'].sum():,.2f}")
with col2:
    st.metric("Total Orders", len(state_sales))
with col3:
    st.metric("Unique States", state_sales['shipstate'].nunique())

logger.info("Metrics displayed")

# Sales Orders Over Time as a Line Chart
st.subheader("Sales Orders Over Time")

# Group by date and calculate total amount for each date
sales_over_time = df_sales.groupby('trandate')['amount'].sum().reset_index()

# Create a line chart for sales orders
line_chart = px.line(sales_over_time, x='trandate', y='amount', title="Sales Orders Over Time")
line_chart.update_layout(
    xaxis_title="Order Date",
    yaxis_title="Total Sales",
    height=400,
    margin=dict(l=40, r=40, t=40, b=40)
)

# Display the chart
st.plotly_chart(line_chart, use_container_width=True)

logger.info("Sales Orders Over Time chart displayed")

# Sales Order Data with Pagination
st.subheader("Filtered Sales Order Data")
page_size = 25
page_number = st.sidebar.number_input("Page Number", min_value=1, max_value=(len(df_sales) // page_size) + 1, value=1, step=1)

# Paginate the DataFrame
start_idx = (page_number - 1) * page_size
end_idx = start_idx + page_size
paginated_df = df_sales[start_idx:end_idx]

st.dataframe(paginated_df)

logger.info("Paginated sales order data displayed")

# Download filtered data
csv = df_sales.to_csv(index=False)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_sales_orders.csv',
    mime='text/csv',
)

logger.info("CSV download button displayed")
