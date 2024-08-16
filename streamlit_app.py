import streamlit as st
import subprocess

# Show title and description
st.title("🔗 Looker-Gsheets Connector")
st.write(
    "XXX"
    "Write explanation"
)

# Ask user for their Looker API client_id and client_secret via `st.text_input`
client_id = st.text_input("Looker API Client ID", type="password")
client_secret = st.text_input("Looker API Client Secret", type="password")

if not client_id or not client_secret:
    st.info("Please add your Looker API Client ID and Client Secret to continue.", icon="🗝️")
else:
    st.success("Credentials provided successfully.")
    
    # Button to execute configuration.py
    if st.button('Run Configuration'):
        try:
            # Run the configuration.py script
            result = subprocess.run(
                ['streamlit', 'run', 'configuration.py'],
                capture_output=True,
                text=True,
                check=True  # Ensure that an exception is raised on error
            )
            # Display the standard output
            st.subheader("Output:")
            st.code(result.stdout, language='python')
            
            # Display the standard error (if any)
            if result.stderr:
                st.subheader("Errors:")
                st.code(result.stderr, language='python')
        
        except subprocess.CalledProcessError as e:
            st.error("An error occurred while running the configuration.")
            st.write("Error message:", e.stderr)
