import streamlit as st

# Define navigation pages with sections (using function names or file paths)
pages = {
    "Main": [  # Main section for general pages
        st.Page("pages/Home.py", title="Home"),
        st.Page("pages/Shipping_Report.py", title="Shipping Report"),

        st.Page("pages/Supply_Chain.py", title="Supply Chain"),

        st.Page("pages/Roles_and_Permissions.py", title="Roles and Permissions"),
        st.Page("pages/Estes_Rate_Generator.py", title="Estes Rate Generator", icon="🌱"),
        st.Page("pages/Barcode_Generator.py", title="Barcode Generator", icon="🌱"),
    ],

    "Practice": [  # Main section for general pages
        st.Page("pages/Practice_Page.py", title="Practice Page", icon="🌱"),
    ],
}

# Configure the sidebar navigation with sections
pg = st.navigation(pages, position="sidebar", expanded=True)

# Run the selected page
pg.run()
