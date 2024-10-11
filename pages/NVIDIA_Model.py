from utils.restlet import fetch_restlet_data
import pandas as pd
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client with NVIDIA API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets["NVIDIA_API_KEY"]
)

# Cache the data fetching process, reset cache every 900 seconds (15 minutes)
@st.cache(ttl=900, show_spinner=False)
def fetch_inventory_data():
    return fetch_restlet_data("customsearch5167")

# Load inventory data
inventory_data = fetch_inventory_data()

def enhance_query_with_inventory_info(user_query):
    # Logic to append/prepend inventory details to the user query
    # This is a simple example; you might need to implement more complex logic
    inventory_summary = inventory_data.describe().to_string()
    enhanced_query = f"{user_query}\n\nInventory Overview:\n{inventory_summary}"
    return enhanced_query

def get_ai_response(enhanced_query):
    completion = client.chat.completions.create(
        model="meta/llama-3.2-3b-instruct",
        messages=[{"role": "user", "content": enhanced_query}],
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
    st.title("Intelligent Inventory Assistant")
    user_input = st.text_input("Ask a question about our inventory:")

    if st.button("Get AI Feedback"):
        if user_input:
            with st.spinner("Generating AI response..."):
                # Enhance the query with inventory data
                enhanced_query = enhance_query_with_inventory_info(user_input)
                # Fetch response from NVIDIA AI
                response = get_ai_response(enhanced_query)
                st.write(response)
        else:
            st.error("Please enter a question to proceed.")

if __name__ == "__main__":
    main()
