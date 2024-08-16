import streamlit as st
import os
import tempfile

# Initial declarations
number_of_looks = None
looks_list = []
look_dict = {}
all_filter = {}
group_filter_0 = {}
group_filter_1 = {}
group_filter_2 = {}
exclude_filters = {
    'all_1': {'filter': [''],'value': ['']}
}
group_filter_0_assignment = []
group_filter_1_assignment = []
group_filter_2_assignment = []
exclude_filters_assignment = []

# Show title and description
st.title("🔗 Looker-Gsheets Connector")
st.write("XXX Write explanation")

# Ask user for their Looker API client_id and client_secret via `st.text_input`
client_id = st.text_input("Looker API Client ID", type="password")
client_secret = st.text_input("Looker API Client Secret", type="password")

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

    # Functions for gathering user input
    def gather_number_of_looks():
        global number_of_looks
        number_of_looks = st.number_input("Enter the number of Looks to be sent:", min_value=1, step=1)

    def gather_look_ids():
        global looks_list
        looks_list = []  # Reset looks_list to avoid appending to old values
        for i in range(number_of_looks):
            look_id = st.text_input(f"Enter ID for look_{i}:").strip()
            if look_id:
                looks_list.append(look_id)

    def gather_tab_names():
        global tab_names
        tab_names = []
        for i in range(number_of_looks):
            tab_name = st.text_input(f"Enter name for gsheet tab_{i}:").strip()
            if tab_name:
                tab_names.append(tab_name)

    def gather_filters_and_values():
        global all_filter
        num_filters = st.number_input("Enter the number of filters to be applied to all Looks:", min_value=0, step=1)
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
        num_filters = st.number_input(f"Enter the number of filters to be applied to Looks in group {group_num}:", min_value=0, step=1)
        for i in range(num_filters):
            filter_key = f"sing_{i+1}"
            filter_input = st.text_input(f"Enter filter 'view_name.field_name' {i+1} for group {group_num}:").strip()
            value_input = st.text_input(f"Enter value for filter {i+1} for group {group_num}:").strip()
            if filter_input and value_input:
                group_filters[group_num][filter_key] = {'filter': [filter_input], 'value': [value_input]}

    def assign_look_ids_to_groups():
        global group_filter_0_assignment, group_filter_1_assignment, group_filter_2_assignment, exclude_filters_assignment
        for index, look_id in enumerate(looks_list):
            assign_filters = st.radio(f"Do you want to assign filters for Look ID {look_id}?", ('Yes', 'No'))
            if assign_filters == 'No':
                continue
            group_choice = st.selectbox(f"Assign Look ID {look_id} to a group:", options=[0, 1, 2, 3], format_func=lambda x: {0: "Group 0 Filters", 1: "Group 1 Filters", 2: "Group 2 Filters", 3: "Exclude from filters"}[x])
            if group_choice == 0:
                group_filter_0_assignment.append(index)
            elif group_choice == 1:
                group_filter_1_assignment.append(index)
            elif group_choice == 2:
                group_filter_2_assignment.append(index)
            elif group_choice == 3:
                exclude_filters_assignment.append(index)

    # Handle user input and configuration
    config_file = st.radio("Do you have a configuration file to upload?", ('Yes', 'No'))

    if config_file == 'Yes':
        uploaded_file = st.file_uploader("Upload a document (.txt)", type=("txt"))
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            if load_config_from_file(content):
                st.success("Configuration loaded successfully.")
            else:
                st.error("Failed to load configuration. Please provide the details manually.")
    else:
        company_domain = st.text_input("Enter the company domain for your Looker instance i.e. 'https://domain.eu.looker.com':").strip()
        gather_number_of_looks()
        gather_look_ids()
        title = st.text_input("Enter the Title of the gsheet you want to send the Looks to:").strip()
        gather_tab_names()
        range_name = st.text_input("Enter the cell where the data should be pasted in the sheets (e.g., 'B2'):").strip()

    # Gather user input for filters and values
    gather_filters_and_values()
    st.write("Three groups of filters can be created (Group 0, Group 1, and Group 2). You will need to determine the number of filters to include in each group:")
    gather_filters_and_values_group(0)
    gather_filters_and_values_group(1)
    gather_filters_and_values_group(2)

    # Assign look IDs to groups
    assign_look_ids_to_groups()

    # Display the configuration summary and filter adjustments
    if st.button('Show Configuration Summary'):
        st.markdown(
        f"""
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
            <p><strong>Company Domain:</strong> {company_domain}</p>
            <p><strong>Number of Looks:</strong> {number_of_looks}</p>
            <p><strong>Look IDs List:</strong> {looks_list}</p>
            <p><strong>Gsheet Title:</strong> {title}</p>
            <p><strong>Tab Names:</strong> {tab_names}</p>
            <p><strong>Cell Range for Pasting Data:</strong> {range_name}</p>
            <p><strong>Filters Applied to All Looks:</strong> {all_filter}</p>
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
