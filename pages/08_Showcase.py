import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation, build_sidebar, get_user_role

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '01_Shipping Report.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

# Build the sidebar based on the user's role and get the selected page
user_role = get_user_role(user_email)
selected_page = build_sidebar(user_role)

# Redirect to the selected page
if selected_page and selected_page != page_name:
    st.experimental_set_query_params(page=selected_page)

# Page content
st.title(f"{user_role} Dashboard - {page_name}")
st.write(f"Welcome, {user_email}!")
st.write(f"You have access to the {user_role} tools on this page.")


################################################################################################

## AUTHENTICATED

################################################################################################

import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
import plotly.express as px

# Set up the page title
st.title("Funnel Conversion, Metrics, and Data Visualization Showcase")

# Sample Data
np.random.seed(42)
data = pd.DataFrame({
    'category': ['A', 'B', 'C', 'D', 'E'] * 20,
    'value': np.random.randint(1, 100, 100),
    'value2': np.random.randn(100).cumsum(),
    'x': np.random.randn(100),
    'y': np.random.randn(100),
    'stage': ['Awareness', 'Interest', 'Decision', 'Action'] * 25,
    'amount': np.random.randint(1, 100, 100),
    'date': pd.date_range(start='1/1/2023', periods=100)
})


# Funnel Chart Data
funnel_data = pd.DataFrame({
    'stage': ['Awareness', 'Interest', 'Decision', 'Action'],
    'amount': [400, 800, 1000, 400]
})

# Calculate Conversion Percentages
funnel_data['conversion'] = funnel_data['amount'].pct_change().fillna(0) * 100
funnel_data['conversion'] = funnel_data['conversion'].apply(lambda x: round(x, 2))

# Funnel Chart using Plotly
st.subheader("Funnel Chart with Conversion Percentages")
funnel_chart = px.funnel(funnel_data, x='stage', y='amount', text='conversion')
funnel_chart.update_traces(texttemplate='%{text:.2s}%')
st.plotly_chart(funnel_chart)

# Metric Boxes with Arrows and Sub-numbers
st.subheader("KPI Metrics")
col1, col2, col3, col4 = st.columns(4)

# Sample metric data for each stage
metrics = [
    {"label": "Awareness", "value": 1000, "change": 10, "positive": True},
    {"label": "Interest", "value": 800, "change": -5, "positive": False},
    {"label": "Decision", "value": 600, "change": -20, "positive": False},
    {"label": "Action", "value": 400, "change": -33.33, "positive": False},
]

# Display dynamic metric boxes with arrows and sub-numbers
for col, metric in zip([col1, col2, col3, col4], metrics):
    arrow = "↑" if metric["positive"] else "↓"
    color = "green" if metric["positive"] else "red"
    
    box_style = """
        background-color: var(--primary-background-color);
        padding: 20px;
        border-radius: 8px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        color: var(--primary-text-color);
    """
    with col:
        st.markdown(f"""
        <div style="{box_style}">
            <h3 style="margin:0;">{metric['label']}</h3>
            <p style="margin:0;font-size:28px;">{metric['value']}</p>
            <p style="margin:0;color:{color};">{arrow} {metric['change']}%</p>
        </div>
        """, unsafe_allow_html=True)

# Data Visualization Showcase Section
st.subheader("Data Visualization Options")

# Bar Chart
st.subheader("Bar Chart")
bar_chart_data = data.groupby('category')['value'].sum().reset_index()
st.bar_chart(bar_chart_data.set_index('category'))

# Line Chart
st.subheader("Line Chart")
st.line_chart(data[['date', 'value2']].set_index('date'))

# Area Chart
st.subheader("Area Chart")
st.area_chart(data[['date', 'value2']].set_index('date'))

# Scatter Plot using Altair
st.subheader("Scatter Plot")
scatter_chart = alt.Chart(data).mark_circle(size=60).encode(
    x='x', 
    y='y', 
    color='category', 
    tooltip=['category', 'x', 'y']
).interactive()
st.altair_chart(scatter_chart, use_container_width=True)

# Pie Chart using Plotly
st.subheader("Pie Chart")
pie_chart = px.pie(data_frame=bar_chart_data, names='category', values='value')
st.plotly_chart(pie_chart)

# Funnel Chart using Plotly
st.subheader("Funnel Chart")
funnel_chart = px.funnel(funnel_data, x='stage', y='amount')
st.plotly_chart(funnel_chart)

# Maps
st.subheader("Map Visualization")
map_data = pd.DataFrame({
    'lat': np.random.uniform(37.76, 37.80, 100),
    'lon': np.random.uniform(-122.4, -122.45, 100)
})
st.map(map_data)

# PyDeck 3D Map
st.subheader("3D Map")
layer = pdk.Layer(
    'HexagonLayer',
    data=map_data,
    get_position=['lon', 'lat'],
    radius=100,
    elevation_scale=4,
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True,
)
view_state = pdk.ViewState(
    latitude=37.76,
    longitude=-122.4,
    zoom=11,
    pitch=50,
)
deck_map = pdk.Deck(layers=[layer], initial_view_state=view_state)
st.pydeck_chart(deck_map)

# Hexbin Alternative using Altair
st.subheader("Density Plot")
density_chart = alt.Chart(data).mark_circle(size=20).encode(
    x='x',
    y='y',
    color='category',
    tooltip=['x', 'y', 'category']
).interactive()
st.altair_chart(density_chart, use_container_width=True)

# Heatmap Visualization using Plotly
st.subheader("Heatmap Visualization")

# Create sample correlation data
heatmap_data = data[['value', 'amount', 'x', 'y']]
corr_matrix = heatmap_data.corr()

# Plot heatmap
heatmap_fig = px.imshow(corr_matrix, 
                        text_auto=True, 
                        aspect="auto", 
                        labels=dict(color="Correlation"),
                        title="Sample Heatmap of Correlations")

st.plotly_chart(heatmap_fig)

# Completion message
st.success("Visualization showcase complete!")
