import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

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

st.write(f"Welcome, {user_email}. You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

from streamlit_echarts import st_echarts

# Simple pie chart to test
test_options = {
    "series": [
        {
            "type": "pie",
            "radius": "50%",
            "data": [
                {"value": 1048, "name": "Tasked Orders"},
                {"value": 735, "name": "Untasked Orders"},
            ],
        }
    ]
}

st_echarts(options=test_options, height="400px")

import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

# Example DataFrame (you would use your actual merged_df DataFrame here)
# Assume merged_df is the DataFrame from the page with a 'Task ID' column
# Fetch raw data (this is part of your page, no need to change)
# merged_df = your_dataframe

# Example structure to mimic your real DataFrame
data = {
    'Order Number': ['001', '002', '003', '004', '005'],
    'Task ID': ['T123', None, 'T125', None, 'T127']
}
merged_df = pd.DataFrame(data)

# Count Tasked vs Untasked records
tasked_count = merged_df['Task ID'].notna().sum()  # Records with Task ID
untasked_count = merged_df['Task ID'].isna().sum()  # Records without Task ID

# Prepare the data for the ECharts pie chart
chart_data = [
    {"value": tasked_count, "name": "Tasked Orders"},
    {"value": untasked_count, "name": "Untasked Orders"}
]

# ECharts Pie chart options
options = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "Task Status",
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2,
            },
            "label": {"show": False, "position": "center"},
            "emphasis": {
                "label": {"show": True, "fontSize": "20", "fontWeight": "bold"}
            },
            "labelLine": {"show": False},
            "data": chart_data,
        }
    ],
}

# Display ECharts Pie Chart in Streamlit
st.subheader("Tasked vs Untasked Orders")
st_echarts(options=options, height="500px")

# Display some metrics (optional, but likely from your original page)
st.write(f"Total Orders: {len(merged_df)}")
st.write(f"Tasked Orders: {tasked_count}")
st.write(f"Untasked Orders: {untasked_count}")
