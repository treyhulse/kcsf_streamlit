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
import pandas as pd
from utils.suiteql import fetch_suiteql_data
from utils.mongo_connection import get_mongo_client, get_collection_data

# Get MongoDB client
client = get_mongo_client()

# Fetch saved queries from 'savedQueries' collection
try:
    saved_queries_df = get_collection_data(client, 'savedQueries')
    if not saved_queries_df.empty:
        # Assuming the DataFrame has columns 'name' and 'query'
        popular_prompts = dict(zip(saved_queries_df['savedQueries'], saved_queries_df['query']))
    else:
        st.error("No saved queries found in the database.")
        popular_prompts = {}
except Exception as e:
    st.error(f"Failed to load saved queries: {e}")
    popular_prompts = {}

# Close the MongoDB client
client.close()

if popular_prompts:
    # Create two columns with specified width ratios
    left_col, right_col = st.columns([3, 1])

    with right_col:
        st.header("Popular Prompts")
        # Display a selection box for prompts
        selected_prompt = st.radio("Select a prompt:", options=list(popular_prompts.keys()))
        st.markdown("---")  # Add a horizontal line for separation

    # Retrieve the SuiteQL script based on the selected prompt
    default_query = popular_prompts[selected_prompt]

    with left_col:
        st.header("SuiteQL Query Input")
        # Text area for users to input or edit SuiteQL scripts
        suiteql_query = st.text_area("Enter your SuiteQL script here:", value=default_query, height=200)

        # Button to execute the query
        if st.button("Run Query"):
            # Execute the SuiteQL script using your fetch_suiteql_data function
            try:
                results_df = fetch_suiteql_data(suiteql_query)
                if not results_df.empty:
                    # Display the results in a table
                    st.subheader("Query Results")
                    st.dataframe(results_df)

                    # Provide a download option
                    csv = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name='query_results.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("No data returned for this query.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.warning("No popular prompts available.")
