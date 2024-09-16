import streamlit as st
import pandas as pd
from datetime import date
from utils.mongo_connection import get_mongo_client, get_collection_data

# Set page configuration with collapsed sidebar
st.set_page_config(
    page_title="KC Store Fixtures",
    page_icon="./assets/KCSF_Square.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Get today's date
today = date.today()

# MongoDB client setup
client = get_mongo_client()

# Fetch announcements from the 'announcements' collection
announcements_data = get_collection_data(client, 'announcements')

# CSS for card styling with drop shadow
st.markdown("""
    <style>
    .card {
        background-color: #ffffff;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        width: 100%;
    }
    .card:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .card h4 {
        margin-top: 0;
        font-size: 1.2rem;
    }
    .card p {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Welcome message and date
st.write(f"# Welcome to KC Store Fixtures! 👋")
st.write(f"**Today's Date:** {today.strftime('%B %d, %Y')}")

# Announcements section - styled as cards with drop shadow
st.write("### Announcements")
if not announcements_data.empty:
    for index, row in announcements_data.iterrows():
        announcement_date = pd.to_datetime(row['date']).strftime('%B %d, %Y')
        st.markdown(
            f"""
            <div class="card">
                <h4>{row['announcement']}</h4>
                <p>Announced on: {announcement_date}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
else:
    st.write("No announcements at this time.")

# Sidebar content
st.sidebar.image("./assets/kcsf_red.png", use_column_width=True)
st.sidebar.success("Select a report above.")

# Main content - Remove 'Available Reports' and add link to website
st.markdown(
    """
    Visit our [KC Store Fixtures App](https://kcstorefixtures.streamlit.app/) for more reports and insights.
    """
)
