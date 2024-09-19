import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

# Set the page configuration
st.set_page_config(
    page_title="Practice Page",
    page_icon="📊",
    layout="wide",
)

# Capture the user's email
user_email = capture_user_email()
if user_email is None:
    st.error("Unable to retrieve user information.")
    st.stop()

# Validate access to this specific page
page_name = 'Order Management'  # Adjust this based on the current page
if not validate_page_access(user_email, page_name):
    show_permission_violation()
    st.stop()

st.write(f"You have access to this page.")

################################################################################################

## AUTHENTICATED

################################################################################################

import streamlit as st

# Function to get user's name (You can replace this with actual user logic)
def get_user_name():
    # For example, this could be fetched from a database or authentication system
    return "User"

# Initialize session state if it doesn't exist
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []

# Get user name
st.experimental_user = get_user_name()

# Welcome Message
st.title(f"Welcome, {st.experimental_user}!")
st.write("This is your file management page. You can upload multiple files, view their content, and manage them effectively within this app. Feel free to drag and drop your files below.")

# File uploader
uploaded_files = st.file_uploader(
    "Upload one or more files by dragging and dropping, or clicking to browse",
    type=None,  # Allow all file types
    accept_multiple_files=True  # Enable multiple file uploads
)

# Add uploaded files to session state
if uploaded_files:
    for file in uploaded_files:
        if file not in st.session_state['uploaded_files']:
            st.session_state['uploaded_files'].append(file)

# Display uploaded files
if st.session_state['uploaded_files']:
    st.subheader("Uploaded Files")
    for file in st.session_state['uploaded_files']:
        st.write(f"File: {file.name}")
        st.write(f"Size: {file.size} bytes")
        
        # Display the content of the file (optional, depending on file type)
        file_type = file.type
        if file_type.startswith("text") or file_type == "application/json":
            st.text(file.getvalue().decode("utf-8"))
        elif file_type.startswith("image"):
            st.image(file)
        else:
            st.write("File type not previewable.")

# Option to clear the uploaded files from session state
if st.button("Clear Uploaded Files"):
    st.session_state['uploaded_files'] = []
    st.success("All uploaded files have been cleared.")
