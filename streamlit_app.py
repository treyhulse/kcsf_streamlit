import streamlit as st

# Define navigation pages with sections (using function names or file paths)
pages = {
    "Main": [  # Main section for general pages
        st.Page("pages/Home.py", title="Home"),
        st.Page("pages/Shipping_Report.py", title="Shipping Report"),


        st.Page("pages/Roles_and_Permissions.py", title="Roles and Permissions"),
        st.Page("pages/Estes_Rate_Generator.py", title="Estes Rate Generator", icon="🌱"),
    ],
}

# Configure the sidebar navigation with sections
pg = st.navigation(pages, position="sidebar", expanded=True)

# Run the selected page
pg.run()
