import streamlit as st
import json

st.set_page_config(page_title="Debug Secrets", page_icon="🔑", layout="wide")

st.title("Debug Secrets")

st.write("This page displays the keys available in `st.secrets` without revealing their values.")

# Get all keys from st.secrets
secret_keys = list(st.secrets.keys())

# Display the number of secrets
st.write(f"Number of secrets available: {len(secret_keys)}")

# Display the keys
st.subheader("Available Secret Keys:")
for key in secret_keys:
    st.write(f"- {key}")

# Add a section to check for specific keys
st.subheader("Check for Specific Keys:")
specific_keys = ['url', 'consumer_key', 'token_key', 'consumer_secret', 'token_secret', 
                 'netsuite_base_url', 'shopify_api_key', 'shopify_admin_api_key', 'shopify_store']

for key in specific_keys:
    if key in st.secrets:
        st.success(f"✅ '{key}' is present in st.secrets")
    else:
        st.error(f"❌ '{key}' is missing from st.secrets")

# Add a section to display secret keys as JSON
st.subheader("Secret Keys as JSON:")
secret_dict = {key: "[HIDDEN]" for key in secret_keys}
st.json(json.dumps(secret_dict, indent=2))

# Add a warning about security
st.warning("⚠️ Remember: Never display the actual values of your secrets in a production environment. This page is for debugging purposes only.")

# Add instructions for adding secrets
st.subheader("How to Add Secrets:")
st.markdown("""
1. **Local Development:**
   - Create a `.streamlit/secrets.toml` file in your project root.
   - Add secrets in the format `key = "value"`.
   - Example:
     ```toml
     url = "https://your-netsuite-restlet-url"
     consumer_key = "your-consumer-key"
     ```

2. **Streamlit Cloud:**
   - Go to your app's settings on Streamlit Cloud.
   - Find the "Secrets" section.
   - Add each secret on a new line in the format `key = value`.

Remember to never commit your `secrets.toml` file to version control!
""")

# Troubleshooting tips
st.subheader("Troubleshooting Tips:")
st.markdown("""
- Ensure all required keys are present in your secrets configuration.
- Check for typos in key names.
- Verify that you're running the app in the correct environment.
- If using Streamlit Cloud, make sure you've saved the secrets in the app settings.
- Restart your Streamlit app after adding new secrets.
""")