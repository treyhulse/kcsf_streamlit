import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(layout="wide")

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Practice Page'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()


st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st
from utils.suiteql import fetch_suiteql_data
import pymongo
import pandas as pd

# MongoDB connection (replace with your MongoDB connection info)
client = pymongo.MongoClient(st.secrets["mongo_uri"])
db = client['netsuite']
collection = db['savedQueries']

# Page Title
st.title("Query Builder and Saved Queries")

# Two columns for layout
col1, col2 = st.columns([2, 1])

# Column 1: Query Input
with col1:
    st.subheader("Enter and Run Queries")

    # Text area for entering user queries
    user_query = st.text_area("Enter your SuiteQL query:", height=200)

    # Run Query button
    if st.button("Run Query"):
        if user_query.strip() == "":
            st.error("Please enter a valid query.")
        else:
            # Execute the query
            df = fetch_suiteql_data(user_query)
            if not df.empty:
                st.write("Query Results")
                st.dataframe(df)
                
                # Option to save query
                with st.expander("Save Query"):
                    query_title = st.text_input("Title your query:")
                    if st.button("Save Query"):
                        if query_title.strip() == "":
                            st.error("Please provide a title for your query.")
                        else:
                            # Save the query to the savedQueries collection in MongoDB
                            query_data = {
                                "title": query_title,
                                "query": user_query
                            }
                            collection.insert_one(query_data)
                            st.success(f"Query '{query_title}' saved successfully!")
            else:
                st.error("No data found for your query.")

# Column 2: Saved Queries
with col2:
    st.subheader("Saved Queries")
    
    # Search saved queries
    search_term = st.text_input("Search for saved queries")
    
    if search_term.strip():
        # Search the MongoDB collection for matching titles
        saved_queries = list(collection.find({"title": {"$regex": search_term, "$options": "i"}}))
    else:
        # Show all saved queries
        saved_queries = list(collection.find())

    if saved_queries:
        # Display the saved queries
        for query in saved_queries:
            st.write(f"**{query['title']}**")
            if st.button(f"Load Query: {query['title']}", key=query['_id']):
                user_query = query['query']  # Load the saved query into the text area
                st.success(f"Loaded query: {query['title']}")
    else:
        st.write("No queries found.")
