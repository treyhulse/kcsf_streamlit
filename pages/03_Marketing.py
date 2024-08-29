import logging
import streamlit as st
from utils.mongo_connection import get_mongo_client, get_collection_data
from st_aggrid import AgGrid, GridOptionsBuilder

# Configure logging for the main page
logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

def main():
    try:
        st.title("MongoDB Sales Collection Viewer")

        # Connect to MongoDB using the utility function
        client = get_mongo_client()

        # Select the collection to display (in this case, always 'sales')
        collection_name = "sales"

        # Get the data from the sales collection using the utility function
        data = get_collection_data(client, collection_name)

        # Display the data with AgGrid for filtering and sorting
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(filterable=True, sortable=True)
        gb.configure_pagination(enabled=True, paginationAutoPageSize=True)  # Enable pagination if needed
        grid_options = gb.build()

        AgGrid(data, gridOptions=grid_options)
    except Exception as e:
        logging.critical(f"Critical error in main function: {e}")
        st.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
