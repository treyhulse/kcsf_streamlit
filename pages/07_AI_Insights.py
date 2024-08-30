import streamlit as st
from openai import OpenAI
from utils.auth import capture_user_email, validate_access, show_permission_violation, get_sidebar_content, get_user_role

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Define roles that can access this page
allowed_roles = ['Sales Manager', 'Administrator']
# Optionally, define roles that cannot access this page
# denied_roles = ['Sales Specialist']

# Validate access
if not validate_access(user_email, allowed_roles=allowed_roles):
    show_permission_violation()

# Sidebar content based on role
user_role = get_user_role(user_email)
st.sidebar.title(f"{user_role} Tools")
sidebar_content = get_sidebar_content(user_role)

for item in sidebar_content:
    st.sidebar.write(item)

# Page content
st.title(f"{user_role} Dashboard")
st.write(f"Welcome, {user_email}!")
st.write(f"You have access to the {user_role} tools.")


################################################################################################

## AUTHENTICATED

################################################################################################

# Show title and description.
st.title("💬 AI Insights")
st.write(
    "Ask me anything! I'm an AI assistant powered by OpenAI's GPT-3.5 model. "
)

# Try to retrieve the API key from secrets, if it doesn't exist, ask the user to input it.
try:
    openai_api_key = st.secrets["openai_api_key"]
except FileNotFoundError:
    openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
