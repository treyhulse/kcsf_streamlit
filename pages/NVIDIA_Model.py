import streamlit as st
import pandas as pd
from openai import OpenAI

# Load CSV data
@st.cache
def load_data():
    df = pd.read_csv("path_to_your_file.csv")
    # Preprocess if necessary (e.g., cleaning, indexing)
    return df

df = load_data()

# Initialize the OpenAI client with NVIDIA API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets["NVIDIA_API_KEY"]
)

def get_ai_response(prompt):
    # Here you could insert logic to search your DataFrame for information
    # relevant to the user's prompt and modify the prompt accordingly.
    # Example:
    # related_info = df[df['column_name'].str.contains(prompt, case=False, na=False)]
    # if not related_info.empty:
    #     prompt += " " + related_info['another_column'].iloc[0]

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
    st.title("NVIDIA AI Enhanced Query Generator")
    user_input = st.text_input("Enter a prompt for the AI:")
    if st.button("Generate"):
        if user_input:
            with st.spinner("AI is generating a response..."):
                response = get_ai_response(user_input)
                st.write(response)
        else:
            st.write("Please enter a prompt to generate a response.")

if __name__ == "__main__":
    main()
