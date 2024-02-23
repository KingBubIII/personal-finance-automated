from os import remove
from json import load, dumps
from easygui import fileopenbox
import csv_ops

# check for a accepted answer
def _good_input_response(answer):
    # make the user response case insensitive
    answer = answer.upper()
    # check for yes or no variations
    if answer in ["YES", "Y", "yes", "y", "NO", "N", "no", "n"]:
        return True
    else:
        return False

def _configs_exist():
    try:
        open('configs.json','r')
        return True
    except FileNotFoundError:
        return False

def _default_configs():
    configs = {"accounts": {}, "categories":{}}

    if not _configs_exist():
        open('configs.json','x')
    else:
        remove('configs.json')

    open('configs.json','x').write(dumps(configs, sort_keys=True, indent=4))
    return True

# decorator to easily add to configs file
def update_configs(func):
    def wrapper(*args, **kwargs):
        if not _configs_exist():
            _default_configs()

        configs = load(open('configs.json','r'))

        # run function with json file contents passed
        configs = func(configs, *args, **kwargs)

        # opens configs file in "write" mode, therefore empties configs file for overwritting later
        with open('configs.json', 'w') as configs_writer:
            # rewrites configs and prettifies output
            configs_writer.write(dumps(configs, sort_keys=True, indent=4))

        return True

    return wrapper

@update_configs
def add_account(configs):
    # asks user input for account identifier and the path the CSV file
    account_name = input('Account nickname: ')
    csv_path = fileopenbox()
    # automatically find columns with names similar to required names
    print(csv_ops.show_csv_columns(csv_path))
    columnIndexes = csv_ops.get_row_indexes( csv_path, {'date': -1, 'amount': -1, 'description': -1})

    # iterate though all column, index pairs
    for col_name, col_index in columnIndexes.items():
        response = ''
        # ask user for input until input is valid
        while not _good_input_response(response):
            if col_index == -1:
                response = input('Could not find a column for {0}, please select a column for it.\n'.format(col_name))
            else:
                response = input('Is {0} the correct column index for {1}? Y/N\n'.format(col_index, col_name))

        if response == "YES" or response == "Y":
            continue
        else:
            while not response.isnumeric():
                response= input('What column should it be for {0}? Y/N\n'.format(col_name))

            columnIndexes[col_name] = int(response)

    configs['accounts'][account_name] = {"csv_path": csv_path, "columnIndexes": columnIndexes}

    return configs

@update_configs
def add_budget_category(configs):
    # get user input for the name of the category
    category_name = input("Name your category: ")
    # adds the category with 3 blanks in a list for the description match, lower limit, upper limit
    configs["categories"][category_name]= []

    return configs

@update_configs
def add_category_rule(configs, category_name):
    description_match = input('Description matching string: ')

    limits = [None, None]

    for index in range(len(limits)):
        try_again = True
        # continue to prompt until a valid input; blank or a number
        while try_again:
            temp_limit = input('Lower limit: ')
            # check for int value
            try:
                limits[index] = int(temp_limit)
                try_again = False
            # error check non-int values
            except ValueError:
                # check for blank value
                if temp_limit == '':
                    limits[index]= None
                    try_again = False

    configs['categories'][category_name].append([description_match, *limits])

    return configs