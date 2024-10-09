import streamlit as st

pages = {
    "Your account": [
        st.Page("Home.py", title="Home"),
        st.Page("01_Shipping_Report.py", title="Shipping Report"),
    ],
    "Resources": [
        st.Page("04_Sales.py", title="Learn about us"),
        st.Page("05_Distributor_Management.py", title="Distributor Management"),
    ],
}

pg = st.navigation(pages)
pg.run()