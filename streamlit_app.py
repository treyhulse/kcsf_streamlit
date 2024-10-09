import streamlit as st

# Define nested pages with groupings
pages = {
    "streamlit app": [
        st.Page("pages/Home.py", title="Home"),
        st.Page("pages/Customer_Portal.py", title="Customer Portal"),
        st.Page("pages/08_Shop.py", title="Shop"),
        st.Page("pages/15_AI_Insights.py", title="AI Insights"),
        st.Page("pages/Role_and_Permissions.py", title="Role and Permissions"),
        st.Page("pages/Pagination_Example.py", title="Pagination Example"),
        st.Page("pages/Practice_Page.py", title="Practice Page"),
        st.Page("pages/MRP_TEST.py", title="MRP TEST"),
        st.Page("pages/Shop_Schedule_Practice.py", title="Shop Schedule Practice"),
    ],
    "Supply Chain": [
        st.Page("pages/02_Supply_Chain.py", title="Supply Chain Overview"),
        st.Page("pages/11_MRP.py", title="MRP"),  # Nested under Supply Chain
    ],
    "Sales": [
        st.Page("pages/04_Sales.py", title="Sales Overview"),
        st.Page("pages/06_Order_Management.py", title="Order Management"),  # Nested under Sales
    ],
    "Support": [
        st.Page("pages/09_Customer_Support.py", title="Customer Support"),
    ],
    "Management": [
        st.Page("pages/05_Distributor_Management.py", title="Distributor Management"),
    ],
    "Logistics": [
        st.Page("pages/01_Shipping_Report.py", title="Shipping Report"),
        st.Page("pages/12_TMS.py", title="Transportation Management System (TMS)"),
    ],
}

# Configure navigation and run the selected page
pg = st.navigation(pages, position="sidebar", expanded=True)

# Run the selected page
pg.run()
