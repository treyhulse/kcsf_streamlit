import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client with NVIDIA API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets["NVIDIA_API_KEY"]
)

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
    st.title("NVIDIA AI Poem Generator")
    user_input = st.text_input("Enter a prompt for the AI:")
    if st.button("Generate"):
        if user_input:
            with st.spinner("AI is generating a poem..."):
                response = get_ai_response(user_input)
                st.write(response)
        else:
            st.write("Please enter a prompt to generate a poem.")

if __name__ == "__main__":
    main()
