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
from pymongo import MongoClient
from utils.mongo_connection import get_mongo_client
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode
import pandas as pd

# Establish MongoDB connection
client = get_mongo_client()
db = client['netsuite']
roles_collection = db['roles']
permissions_collection = db['permissions']

def admin_ui():
    st.title("Role and Permissions Management")

    st.markdown("---")

    # Section 1: View and Edit Current Roles and Emails
    st.subheader("Current Roles and Emails")
    roles_data = list(roles_collection.find())
    
    # Convert MongoDB data to DataFrame
    roles_df = pd.DataFrame(roles_data)
    if not roles_df.empty:
        roles_df["_id"] = roles_df["_id"].astype(str)  # Convert ObjectId to string

    # Editable table using streamlit-aggrid
    gb = GridOptionsBuilder.from_dataframe(roles_df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Enable pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection('multiple', use_checkbox=True)  # Enable multi-row selection
    gb.configure_grid_options(editable=True)  # Make grid editable
    grid_options = gb.build()

    grid_response = AgGrid(
        roles_df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True,
        height=400,
        width='100%',
    )

    updated_df = grid_response['data']
    selected_rows = grid_response['selected_rows']

    if st.button("Update Roles"):
        # Iterate through the updated DataFrame and update MongoDB
        for _, row in updated_df.iterrows():
            roles_collection.update_one(
                {"_id": row["_id"]},
                {"$set": {"role": row["role"], "emails": row["emails"]}}
            )
        st.success("Roles updated successfully.")

    st.markdown("---")

    # Existing code for adding, removing roles/emails and updating permissions
    # ...

if __name__ == "__main__":
    user_email = capture_user_email()
    if user_email is None:
        st.error("Unable to retrieve user information.")
        st.stop()

    page_name = '09_Role_Permissions.py'

    if validate_page_access(user_email, page_name):
        admin_ui()
    else:
        show_permission_violation()
