import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Looker Test")
st.write(
    "XXX"
    "Write explanation"
)

# Ask user for their Looker API keys via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
client_id = st.text_input("Looker API Key", type="password")
if not client_id:
    st.info("Please add your Looker API keys to continue. (Client ID & Secret)", icon="🗝️")
else:

    
