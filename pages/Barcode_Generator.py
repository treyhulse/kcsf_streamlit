import streamlit as st
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
