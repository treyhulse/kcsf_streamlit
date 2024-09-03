import streamlit as st
from st_pages import add_page_title, get_nav_from_toml

sections = st.sidebar.toggle("Sections", value=True, key="use_sections")

nav = get_nav_from_toml(
    ".streamlit/pages_sections.toml" if sections else ".streamlit/pages.toml"
)

st.logo("./assets/kcsf_red.png")

pg = st.navigation(nav)

add_page_title(pg)

pg.run()