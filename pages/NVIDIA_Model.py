from utils.restlet import fetch_restlet_data
import pandas as pd
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client with NVIDIA API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets["NVIDIA_API_KEY"]
)

# Cache the raw data fetching process, reset cache every 15 minutes (900 seconds)
@st.cache(ttl=900, allow_output_mutation=True)  # Using `allow_output_mutation=True` as a potential fix for caching mutable objects
def fetch_raw_data(saved_search_id):
    # Fetch raw data from RESTlet without filters
    return fetch_restlet_data(saved_search_id)

# Sidebar filters
st.sidebar.header("Filters")

# Fetch raw data
inventory_data = fetch_raw_data("customsearch5122")

def get_ai_response(prompt):
    completion = client.chat.completions.create(
        model="meta/llama-3.2-3b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )

    response = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content
    return response

def main():
    st.title("NVIDIA AI Inventory Assistant")
    user_input = st.text_input("Enter your query about our inventory:")
    if st.button("Submit"):
        if user_input:
            with st.spinner("Generating AI response..."):
                response = get_ai_response(user_input)
                st.write(response)
        else:
            st.error("Please enter a query to get a response.")

if __name__ == "__main__":
    main()
