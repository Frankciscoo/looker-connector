import streamlit as st
import subprocess

# Show title and description.
st.title("🔗 Looker-Gsheets Connector")
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
    
    # Button to execute configuration.py
    if st.button('Run Configuration'):
        try:
            result = subprocess.run(['streamlit', 'run', 'configuration.py'], capture_output=True, text=True)
            # Print the standard output
            print("Output:")
            print(result.stdout)
            # Print the standard error (if any)
            print("Errors:")
            print(result.stderr)
            # Check the return code
            if result.returncode != 0:
                print(f"Streamlit run failed with return code {result.returncode}")
        else:
            print("Streamlit run succeeded")
                except subprocess.CalledProcessError as e:
                    st.error("An error occurred while running the configuration.")
                    st.write("Error message:", e.stderr)
