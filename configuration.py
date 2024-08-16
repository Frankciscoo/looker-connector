import os

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

# Function to load configuration from file
def load_config_from_file(filename):
    global number_of_looks, looks_list, title, tab_names, range_name, company_domain

    if not os.path.isfile(filename):
        print(f"Configuration file '{filename}' does not exist.")
        return False

    with open(filename, 'r') as file:
        config = file.read().splitlines()
        config_dict = {}
        for line in config:
            key, value = line.split('=', 1)
            config_dict[key.strip()] = value.strip()

        company_domain = config_dict.get('company_domain', '')
        number_of_looks = int(config_dict.get('number_of_looks', '0'))
        looks_list = config_dict.get('looks_list', '').split(',')
        title = config_dict.get('title', '')
        tab_names = config_dict.get('tab_names', '').split(',')
        range_name = config_dict.get('range_name', '')

    return True

# Function to gather user input for number of looks
def gather_number_of_looks():
    global number_of_looks
    number_of_looks = int(input("Enter the number of Looks to be sent: "))

# Function to gather user input for each look ID
def gather_look_ids():
    global looks_list
    for i in range(number_of_looks):
        look_ids = input(f"Enter IDs for look_{i}: ").strip()
        looks_list.append(look_ids)
        globals()[f"look_{i}"] = look_ids  # Dynamically create variables

# Function to gather user input for tab names
def gather_tab_names():
    global tab_names
    tab_names = []
    for i in range(number_of_looks):
        tab_name = input(f"Enter name for gsheet tab_{i}: ").strip()
        tab_names.append(tab_name)
        globals()[f"name_tab_{i}"] = tab_name  # Dynamically create variables

# Functions to gather user input for filters and values
def gather_filters_and_values():
    global all_filter
    num_filters = int(input("Enter the number of filters to be applied to all Looks: "))
    for i in range(num_filters):
        filter_key = f"all_{i+1}"
        filter_input = input(f"Enter filter 'view_name.field_name' {i+1}: ").strip()
        value_input = input(f"Enter value for filter {i+1}: ").strip()
        all_filter[filter_key] = {'filter': [filter_input], 'value': [value_input]}

def gather_filters_and_values_group(group_num):
    global group_filter_0, group_filter_1, group_filter_2
    group_filters = [group_filter_0, group_filter_1, group_filter_2]
    num_filters = int(input(f"Enter the number of filters to be applied to Looks in group {group_num}: "))

    for i in range(num_filters):
        filter_key = f"sing_{i+1}"
        filter_input = input(f"Enter filter 'view_name.field_name' {i+1} for group {group_num}: ").strip()
        value_input = input(f"Enter value for filter {i+1} for group {group_num}: ").strip()
        group_filters[group_num][filter_key] = {'filter': [filter_input], 'value': [value_input]}

# Function to assign look IDs to groups
def assign_look_ids_to_groups():
    for index, look_id in enumerate(looks_list):
        assign_filters = input(f"Do you want to assign filters for Look ID {look_id}? (y/n): ").strip().lower()
        if assign_filters == 'n':
            continue

        while True:
            print(f"Assign Look ID {look_id} to a group:")
            print("0 - Group 0 Filters")
            print("1 - Group 1 Filters")
            print("2 - Group 2 Filters")
            print("3 - Exclude from filters")
            group_choice = input("Enter the number corresponding to the group: ").strip()

            if group_choice == '0':
                group_filter_0_assignment.append(index)
                break
            elif group_choice == '1':
                group_filter_1_assignment.append(index)
                break
            elif group_choice == '2':
                group_filter_2_assignment.append(index)
                break
            elif group_choice == '3':
                exclude_filters_assignment.append(index)
                break
            else:
                print("Invalid input, please enter a number between 0 and 3.")

# Main program flow
config_file = input("Do you have a configuration file to upload? (y/n): ").strip().lower()

if config_file == 'y':
    filename = input("Enter the path to the configuration file: ").strip()
    if load_config_from_file(filename):
        print("Configuration loaded successfully.")
    else:
        print("Failed to load configuration. Please provide the details manually.")
else:
    company_domain = input("Enter the company domain for your Looker instance i.e. 'https://domain.eu.looker.com': ").strip()
    gather_number_of_looks()
    gather_look_ids()
    title = input("Enter the Title of the gsheet you want to send the Looks to: ").strip()
    gather_tab_names()
    range_name = input("Enter the cell where the data should be pasted in the sheets (e.g., 'B2'): ").strip()

# Debug print statements to verify the input
print()
print("--Configuration Summary--")
print("Company Domain:", company_domain)
print("Number of Looks:", number_of_looks)
print("Look IDs List:", looks_list)
print("Gsheet Title:", title)
print("Tab Names:", tab_names)
print("Cell Range for Pasting Data:", range_name)
