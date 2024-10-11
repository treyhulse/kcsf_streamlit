import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key="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"
)

# Define a function to get my response
def get_response(prompt):
  completion = client.chat.completions.create(
    model="meta/llama-3.2-3b-instruct",
    messages=[{"role":"user","content":prompt}],
    temperature=0.2,
    top_p=0.7,
    max_tokens=1024,
    stream=True
  )

  for chunk in completion:
    if chunk.choices[0].delta.content is not None:
      return chunk.choices[0].delta.content

# Create a Streamlit app
st.title("My AI Model")

# Add a text input component
prompt = st.text_input("Enter your question or prompt")

# Call the get_response function
response = get_response(prompt)

# Display my response
st.write("My response:")
st.write(response)
