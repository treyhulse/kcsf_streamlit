import streamlit as st

# Set page configuration must be the first Streamlit command
st.set_page_config(
    page_title="KCSF Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation setup
pages = [
    st.Page("pages/Home.py", title="Home"),
    st.Page("pages/Shipping_Report.py", title="Shipping Report"),
    st.Page("pages/Roles_and_Permissions.py", title="Roles and Permissions"),
    st.Page("pages/Estes_Rate_Generator.py", title="Estes Rate Generator")
]

pg = st.navigation(pages)
pg.run()
