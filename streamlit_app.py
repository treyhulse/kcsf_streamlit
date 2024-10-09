import streamlit as st

# Define navigation pages with sections (using function names or file paths)
pages = {
    "Main": [  # Main section for general pages
        st.Page("pages/Home.py", title="Home", icon="🏠"),
        st.Page("pages/Customer_Portal.py", title="Customer Portal", icon="👤"),
        st.Page("pages/Shop.py", title="Shop", icon="🛠️"),
        st.Page("pages/AI_Insights.py", title="AI Insights", icon="💬"),
        st.Page("pages/Role_and_Permissions.py", title="Role and Permissions", icon="🔒"),
        st.Page("pages/Pagination_Example.py", title="Pagination Example", icon="📄"),
        st.Page("pages/Practice_Page.py", title="Practice Page", icon="🌱"),
        st.Page("pages/MRP_TEST.py", title="MRP TEST", icon="🌱"),
        st.Page("pages/Shop_Schedule_Practice.py", title="Shop Schedule Practice", icon="🌱"),
    ],
    "Supply Chain": [  # Section title for Supply Chain
        st.Page("pages/Supply_Chain.py", title="Supply Chain Overview", icon="🚚"),
        st.Page("pages/MRP.py", title="Material Resource Planning", icon="📦"),
    ],
    "Sales": [  # Section title for Sales
        st.Page("pages/Sales.py", title="Sales Overview", icon="💲"),
        st.Page("pages/Order_Management.py", title="Order Management", icon="💰"),
    ],
    "Support": [  # Section title for Support
        st.Page("pages/Customer_Support.py", title="Customer Support", icon="📞"),
    ],
    "Management": [  # Section title for Management
        st.Page("pages/Distributor_Management.py", title="Distributor Management", icon="👥"),
    ],
    "Logistics": [  # Section title for Logistics
        st.Page("pages/Shipping_Report.py", title="Shipping Report", icon="🚚"),
        st.Page("pages/TMS.py", title="Transportation Management System", icon="🌐"),
    ],
}

# Configure the sidebar navigation with sections
pg = st.navigation(pages, position="sidebar", expanded=True)

# Run the selected page
pg.run()
