import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = '09_Role_Permissions.py'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from utils.mongo_connection import get_mongo_client, get_collection_data

# Initialize MongoDB client
client = get_mongo_client()

# Function to display an editable table and update MongoDB
def display_editable_table(collection_name):
    st.subheader(f"{collection_name.capitalize()} Collection")
    
    # Fetch data from MongoDB
    df = get_collection_data(client, collection_name)
    
    if not df.empty:
        df["_id"] = df["_id"].astype(str)  # Convert ObjectId to string for display

    # Create an editable grid with streamlit-aggrid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Enable pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection('multiple', use_checkbox=True)  # Enable multi-row selection
    gb.configure_grid_options(editable=True)  # Make the grid editable
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True,
        height=400,
        width='100%',
    )

    updated_df = grid_response['data']  # Get the DataFrame after editing

    if st.button(f"Publish Changes to {collection_name.capitalize()}"):
        collection = client['netsuite'][collection_name]
        for index, row in updated_df.iterrows():
            # Update MongoDB document by _id
            collection.update_one(
                {"_id": row["_id"]},
                {"$set": row.to_dict()}
            )
        st.success(f"Changes published to {collection_name.capitalize()} collection.")

# Streamlit app layout
st.title("MongoDB Editable Table")

st.markdown("### Edit Roles and Permissions Collections")

# Display editable table for Roles collection
display_editable_table('roles')

st.markdown("---")

# Display editable table for Permissions collection
display_editable_table('permissions')
