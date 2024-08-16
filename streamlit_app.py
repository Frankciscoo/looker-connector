import streamlit as st

# Show title and description.
st.title("🔗 Looker Connector")
st.write(
    "XXX"
    "Write explanation"
)

# Ask user for their Looker API client_id and client_secret via `st.text_input`.
client_id = st.text_input("Looker API Client ID", type="password")
client_secret = st.text_input("Looker API Client Secret", type="password")

if not client_id or not client_secret:
    st.info("Please add your Looker API Client ID and Client Secret to continue.", icon="🗝️")
else:
    st.success("Credentials provided successfully.")
    # Proceed with the rest of your code here...


    
