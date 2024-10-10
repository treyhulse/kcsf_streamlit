import streamlit as st

# Define navigation pages with sections (using function names or file paths)
pages = {
    "Main": [  # Main section for general pages
        st.Page("pages/Home.py", title="Home"),
        st.Page("pages/Shipping_Report.py", title="Shipping Report"),
        st.Page("pages/TMS.py", title="Transportation Management System"),

        st.Page("pages/Supply_Chain.py", title="Supply Chain"),
        st.Page("pages/MRP.py", title="Material Resource Planning"),
        st.Page("pages/Shop_Schedule.py", title="Shop Schedule"),

        st.Page("pages/Sales.py", title="Sales Dashboard"),
        st.Page("pages/Order_Management.py", title="Order Management"),
        st.Page("pages/Distributor_Management.py", title="Distributor Management"),
        st.Page("pages/Customer_Portal.py", title="Customer Portal"),
        st.Page("pages/Customer_Support.py", title="Support"),
        st.Page("pages/AI_Insights.py", title="AI Insights"),
        st.Page("pages/Roles_and_Permissions.py", title="Roles and Permissions"),
        st.Page("pages/Estes_Rate_Generator.py", title="Estes Rate Generator", icon="🌱"),

    ],

    "Practice": [  # Main section for general pages
        st.Page("pages/Pagination_Example.py", title="Pagination Example", icon="🌱"),
        st.Page("pages/Practice_Page.py", title="Practice Page", icon="🌱"),
        st.Page("pages/MRP_TEST.py", title="MRP TEST", icon="🌱"),
    ],
}

# Configure the sidebar navigation with sections
pg = st.navigation(pages, position="sidebar", expanded=True)

# Run the selected page
pg.run()
