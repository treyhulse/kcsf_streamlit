import streamlit as st
from utils.auth import capture_user_email, validate_page_access, show_permission_violation

st.set_page_config(page_title="Barcode Generator", 
                   layout="wide",)

# Custom CSS to hide the top bar and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
import io

st.title("Barcode Generator")

# User input
text_input = st.text_input("Enter text to generate barcode:")

if text_input:
    # Generate barcode
    barcode = Code128(text_input, writer=ImageWriter())
    
    # Save barcode to an in-memory file
    buffer = io.BytesIO()
    barcode.write(buffer)
    
    # Load the image from buffer and display it
    barcode_image = Image.open(buffer)
    st.image(barcode_image, caption="Generated Barcode")
    
    # Provide download option
    buffer.seek(0)
    st.download_button(
        label="Download Barcode",
        data=buffer,
        file_name=f"{text_input}_barcode.png",
        mime="image/png"
    )
