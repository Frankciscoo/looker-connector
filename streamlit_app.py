import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import json
import requests

# Initial declarations
number_of_looks = None
looks_list = []
look_dict = {}
all_filter = {}
group_filter_0 = {}
group_filter_1 = {}
group_filter_2 = {}
exclude_filters = {
    'all_1': {'filter': [''], 'value': ['']}
}
group_filter_0_assignment = []
group_filter_1_assignment = []
group_filter_2_assignment = []
exclude_filters_assignment = []
company_domain = ""  # Initialize to avoid NameError

group_filter_assignments = [
    group_filter_0_assignment,
    group_filter_1_assignment,
    group_filter_2_assignment
]

group_filters = {
    'group_filter_0': group_filter_0,
    'group_filter_1': group_filter_1,
    'group_filter_2': group_filter_2
}

# Show title and description
st.title("🔗 Looker-gsheets connector")
st.write("XXX Write explanation")
st.header("API Credentials", divider=True)

# Ask user for their Looker API client_id and client_secret via st.text_input
client_id = st.text_input("**Looker API :blue[Client ID]**", type="password")
client_secret = st.text_input("**Looker API :blue[Client Secret]**", type="password")

if not client_id or not client_secret:
    st.info("Please add your Looker API Client ID and Client Secret to continue.", icon="🗝️")
else:
    st.success("Credentials provided successfully!")

    # Load configuration function
    def load_config_from_file(file_content):
        global number_of_looks, looks_list, title, tab_names, range_name, company_domain
        config = file_content.splitlines()
        config_dict = {}
        for line in config:
            if '=' in line:
                key, value = line.split('=', 1)
                config_dict[key.strip()] = value.strip()
        company_domain = config_dict.get('company_domain', '')
        number_of_looks = int(config_dict.get('number_of_looks', '0'))
        looks_list = config_dict.get('looks_list', '').split(',')
        title = config_dict.get('title', '')
        tab_names = config_dict.get('tab_names', '').split(',')
        range_name = config_dict.get('range_name', '')
        return True

    def load_filters_from_file(file_content):
        global all_filter, group_filter_0, group_filter_1, group_filter_2
        filters = file_content.splitlines()
        filter_dict = {}
        current_group = None

        for line in filters:
            if line.startswith("Group"):
                current_group = int(line.split()[1])
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().split(',')
                if current_group is None:
                    filter_dict[key] = {'filter': value, 'value': value}
                else:
                    if current_group == 0:
                        group_filter_0[key] = {'filter': value, 'value': value}
                    elif current_group == 1:
                        group_filter_1[key] = {'filter': value, 'value': value}
                    elif current_group == 2:
                        group_filter_2[key] = {'filter': value, 'value': value}
        all_filter = filter_dict
        return True

    # Functions for gathering user input
    def gather_number_of_looks():
        global number_of_looks
        number_of_looks = st.number_input("Enter the :blue[number of Looks] to be sent:", min_value=1, step=1)

    def gather_look_ids():
        global looks_list
        looks_list = []  # Reset looks_list to avoid appending to old values
        for i in range(number_of_looks):
            look_id = st.text_input(f"Enter ID for :blue[look_{i}]:").strip()
            if look_id:
                looks_list.append(look_id)

    def gather_tab_names():
        global tab_names
        tab_names = []
        for i in range(number_of_looks):
            tab_name = st.text_input(f"Enter name for :blue[gsheet tab_{i}]:").strip()
            if tab_name:
                tab_names.append(tab_name)

    def gather_filters_and_values():
        global all_filter
        num_filters = st.number_input("Enter the :blue[number of filters] to be applied to :blue[all Looks]:", min_value=0, step=1)
        st.error("These filters will be applied to all Looks unless they are marked as 'Exclude from filters", icon="⚠️")
        all_filter = {}  # Initialize the dictionary to avoid appending to old values
        for i in range(num_filters):
            filter_key = f"all_{i+1}"
            filter_input = st.text_input(f"Enter filter 'view_name.field_name' {i+1}:").strip()
            value_input = st.text_input(f"Enter value for filter {i+1}:").strip()
            if filter_input and value_input:
                all_filter[filter_key] = {'filter': [filter_input], 'value': [value_input]}

    def gather_filters_and_values_group(group_num):
        global group_filter_0, group_filter_1, group_filter_2
        group_filters = [group_filter_0, group_filter_1, group_filter_2]
        num_filters = st.number_input(f"Enter the :blue[number of filters] to be applied to Looks in :blue[group {group_num}]:", min_value=0, step=1)
        for i in range(num_filters):
            filter_key = f"sing_{i+1}"
            filter_input = st.text_input(f"Enter :blue[filter 'view_name.field_name' {i+1}] for :blue[group {group_num}]:").strip()
            value_input = st.text_input(f"Enter :blue[value for filter {i+1}] for :blue[group {group_num}]:").strip()
            if filter_input and value_input:
                group_filters[group_num][filter_key] = {'filter': [filter_input], 'value': [value_input]}

    def assign_look_ids_to_groups():
        global group_filter_0_assignment, group_filter_1_assignment, group_filter_2_assignment, exclude_filters_assignment
        for index, look_id in enumerate(looks_list):
            assign_filters = st.radio(f"Do you want to :blue[assign filters] for :blue[Look ID {look_id}]?", ('Yes', 'No'))
            if assign_filters == 'No':
                continue
            group_choice = st.selectbox(f":blue[Assign Look ID {look_id}] to a :blue[group]:", options=[0, 1, 2, 3], format_func=lambda x: {0: "Group 0 Filters", 1: "Group 1 Filters", 2: "Group 2 Filters", 3: "Exclude from filters"}[x])
            if group_choice == 0:
                group_filter_0_assignment.append(index)
            elif group_choice == 1:
                group_filter_1_assignment.append(index)
            elif group_choice == 2:
                group_filter_2_assignment.append(index)
            elif group_choice == 3:
                exclude_filters_assignment.append(index)

    # Handle user input and configuration
    st.header("Configuration", divider=True)
    config_file = st.radio("**Do you have a :blue[configuration file] to upload?**", ('Yes', 'No'))

    if config_file == 'Yes':
        uploaded_file = st.file_uploader("Upload a document (.txt)", type=("txt"))
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            if load_config_from_file(content):
                st.success("Configuration loaded successfully.")
            else:
                st.error("Failed to load configuration. Please provide the details manually.")
    else:
        company_domain = st.text_input("Enter the :blue[company domain] for your Looker instance i.e. 'https://domain.eu.looker.com':").strip()
        gather_number_of_looks()
        gather_look_ids()
        title = st.text_input("Enter the :blue[Title of the gsheet] you want to send the Looks to:").strip()
        gather_tab_names()
        range_name = st.text_input("Enter the :blue[cell] where the data should be pasted in the sheets (e.g., 'B2'):").strip()

    # Main function to handle OAuth flow
    def main():
        # Clear previous session state if needed
        if 'credentials' in st.session_state:
            del st.session_state['credentials']
    
        try:
            # Access credentials from Streamlit secrets
            client_id = st.secrets["google"]["client_id"]
            client_secret = st.secrets["google"]["client_secret"]
    
            # Define the client configuration dictionary WITHOUT redirect_uri
            client_config = {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "project_id": st.secrets["google"]["project_id"]
                }
            }
    
            # Define the OAuth flow with the required scopes
            flow = Flow.from_client_config(
                client_config,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",        # Full access to Google Sheets
                    "https://www.googleapis.com/auth/drive.metadata.readonly" # Read-only access to file metadata in Google Drive
                ],
                redirect_uri="http://localhost:8501/"
            )
    
            # Generate the authorization URL, explicitly setting the redirect_uri only here
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            st.write(f"Visit this [link]({authorization_url}) to grant access to your gsheet:")
    
            # Input field for the code received after authentication
            code = st.text_input("Enter the code generated in the URL :blue['code=']")
            
            if code:
                # Exchange the authorization code for a token
                flow.fetch_token(code=code)
                credentials = flow.credentials
    
                st.success("Authentication successful")
    
                # Store credentials in the session state
                st.session_state.credentials = credentials
    
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    if __name__ == "__main__":
        main()

    # Handle filters input or upload
    st.header("Filters", divider=True)
    filters_file = st.radio("**Do you have a :blue[filters file] to upload?**", ('Yes', 'No'))

    if filters_file == 'Yes':
        filters_uploaded_file = st.file_uploader("Upload filters document (.txt)", type=("txt"))
        if filters_uploaded_file:
            filters_content = filters_uploaded_file.read().decode('utf-8')
            if load_filters_from_file(filters_content):
                st.success("Filters loaded successfully.")
                st.divider()
            else:
                st.error("Failed to load filters. Please provide the details manually.")
                st.divider()
    else:
        gather_filters_and_values()
        st.info("Three groups of filters can be created (Group 0, Group 1, and Group 2). You will need to determine the number of filters to include in each group:", icon="ℹ️")
        gather_filters_and_values_group(0)
        gather_filters_and_values_group(1)
        gather_filters_and_values_group(2)

        # Assign look IDs to groups
        assign_look_ids_to_groups()

    # Initialize session state variable if it doesn't exist
    if 'show_summary' not in st.session_state:
        st.session_state.show_summary = False
    
    # Button to toggle the visibility of the configuration summary
    if st.button('Show Configuration Summary'):
        st.session_state.show_summary = not st.session_state.show_summary
    
    # Display the configuration summary if the state is True
    if st.session_state.show_summary:
        st.markdown(
        f"""
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
            <p><strong>Company Domain:</strong> {company_domain}</p>
            <p><strong>Number of Looks:</strong> {number_of_looks}</p>
            <p><strong>Look IDs List:</strong> {looks_list}</p>
            <p><strong>Gsheet Title:</strong> {title}</p>
            <p><strong>Tab Names:</strong> {tab_names}</p>
            <p><strong>Cell Range for Pasting Data:</strong> {range_name}</p>
            <p><strong>Filters Applied to all Looks:</strong> {all_filter}</p>
            <p><strong>Group 0 Filters:</strong> {group_filter_0}</p>
            <p><strong>Group 1 Filters:</strong> {group_filter_1}</p>
            <p><strong>Group 2 Filters:</strong> {group_filter_2}</p>
            <p><strong>Group 0 Assignments:</strong> {group_filter_0_assignment}</p>
            <p><strong>Group 1 Assignments:</strong> {group_filter_1_assignment}</p>
            <p><strong>Group 2 Assignments:</strong> {group_filter_2_assignment}</p>
            <p><strong>Exclude Filters Assignments:</strong> {exclude_filters_assignment}</p>
        </div>
        """,
        unsafe_allow_html=True)

    st.header("Filter check!", divider=True)

    def generate_auth_token():
        data = {
            'client_id': client_id,
            'client_secret': client_secret
        }
        auth_token = requests.post(f'{company_domain}:19999/api/4.0/login', data=data)
        return auth_token.json().get('access_token')
    
    HEADERS = {
        'Authorization': 'token {}'.format(generate_auth_token())
    }
    URL = f'{company_domain}:19999/api/4.0/'

    def get_model_view(look_id):
        read_look = requests.get(f"{URL}looks/{look_id}", headers=HEADERS)
        json_data = read_look.json()
        model = json_data.get('query', {}).get('model')
        view = json_data.get('query', {}).get('view')
        return model, view
    
    def get_fields_from_explore(lookml_model_name, explore_name):
        read_look = requests.get(f"{URL}lookml_models/{lookml_model_name}/explores/{explore_name}", headers=HEADERS)
        json_data = read_look.json()
        dimensions = [item.get('name') for item in json_data.get('fields', {}).get('dimensions', [])]
        measures = [item.get('name') for item in json_data.get('fields', {}).get('measures', [])]
        parameters = [item.get('name') for item in json_data.get('fields', {}).get('parameters', [])]
        return dimensions, measures, parameters

    def check_filters_in_explores(explore_fields, all_filter, group_filters, group_filter_assignments, exclude_filters_assignment):
        missing_filters = {}

        def check_filter_against_explores(filter_name, explore_key, explore_value):
            if filter_name == '':
                return

            dimensions = explore_value['dimensions']
            measures = explore_value['measures']
            parameters = explore_value['parameters']

            if (filter_name not in dimensions and
                    filter_name not in measures and
                    filter_name not in parameters):

                if explore_key not in missing_filters:
                    missing_filters[explore_key] = []
                missing_filters[explore_key].append(filter_name)

        assignments = {}
        for i, assignment in enumerate(group_filter_assignments):
            for assignment_value in assignment:
                if assignment_value is not None:
                    if f'group_filter_{i}' not in assignments:
                        assignments[f'group_filter_{i}'] = []
                    assignments[f'group_filter_{i}'].append(assignment_value)

        for filter_key, filter_value in all_filter.items():
            filter_name = filter_value['filter'][0]

            for explore_key, explore_value in explore_fields.items():
                check_filter_against_explores(filter_name, explore_key, explore_value)

        for group_key, group_filter in group_filters.items():
            explore_keys = assignments.get(group_key)
            if explore_keys is not None:
                for explore_key in explore_keys:
                    explore_value = explore_fields.get(explore_key)
                    if explore_value:
                        for filter_key, filter_value in group_filter.items():
                            filter_name = filter_value['filter'][0]
                            check_filter_against_explores(filter_name, explore_key, explore_value)

        if not missing_filters:
            st.success("Filters can be applied to all Looks!")
        else:
            for explore_key, filters in missing_filters.items():
                warning_message = (
                    f"Warning: Missing/Incorrect filter(s) {filters} in explore from look #: {explore_key}"
                )
                st.error(warning_message)

    def update_google_sheet(credentials):
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open(title)
        return spreadsheet
    
    # Create a DataFrame from looks_list
    looks = pd.DataFrame(np.array(looks_list).reshape(-1, 1), columns=['look_id'])
    # Check the Looker filters
    if st.button('Check Filters'):
        # Get the models & views from each look
        explores = {}
        for i in range(number_of_looks):
            tab_name = globals().get(f"name_tab_{i}")
            if tab_name:
                globals()[f"tab_{i}"] = sheet.worksheet(tab_name)
            explores[i] = get_model_view(looks.loc[i, "look_id"])
    
        # Get all the fields from each explore (model - view)
        explore_fields = {}
        for key, (lookml_model_name, explore_name) in explores.items():
            dimensions, measures, parameters = get_fields_from_explore(lookml_model_name, explore_name)
            explore_fields[key] = {'dimensions': dimensions, 'measures': measures, 'parameters': parameters}
    
        # Check filters and display result
        result = check_filters_in_explores(explore_fields, all_filter, group_filters, group_filter_assignments, exclude_filters_assignment)
