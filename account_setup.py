from easygui import fileopenbox
import csv_ops

from user_input_validation import valid_YN_response, user_confirmed
from configs_ops import update_configs

def defaults(headers=False, rules=False) -> list[str]:
    if headers:
        return ['date', 'amount', 'description']
    elif rules:
        return ['Misc']

@update_configs
def add_account(configs):
    # asks user input for account identifier and the path the CSV file
    account_name = input('Account nickname: ')
    csv_path = fileopenbox()
    # automatically find columns with names similar to required names
    print(csv_ops.show_csv_columns(csv_path))
    # finds all relavant headers determined by passed class definition
    # passes csv file path and a dictionary of each header with a value of -1
    columnIndexes = csv_ops.get_row_indexes( csv_path,  {header:-1 for header in defaults(headers=True)})

    # iterate though all column, index pairs
    for col_name, col_index in columnIndexes.items():
        response = ''
        # ask user for input until input is valid
        while not valid_YN_response(response):
            if col_index == -1:
                response = input('Could not find a column for {0}, please select a column for it.\n'.format(col_name))
            else:
                response = input('Is {0} the correct column index for {1}? Y/N\n'.format(col_index, col_name))

        if not user_confirmed(response):
            while not response.isnumeric():
                response= input('What column should it be for {0}? Y/N\n'.format(col_name))

            columnIndexes[col_name] = int(response)

    configs['accounts'][account_name] = {"csv_path": csv_path, "columnIndexes": columnIndexes}

    return configs

@update_configs
def add_category(configs):
    # get user input for the name of the rule
    category_name = input("Name your category: ")
    # adds the rule with 3 blanks in a list for the description match, lower limit, upper limit
    configs["categories"].append(category_name)

    return configs

@update_configs
def add_rule(configs, category_name):
    if category_name in configs["categories"]:
        description_match = input('Description matching string: ')

        limits = [None, None]

        for index in range(len(limits)):
            try_again = True
            # continue to prompt until a valid input; blank or a number
            while try_again:
                temp_limit = input('{0} limit: '.format("Lower" if index==0 else "Upper"))
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

        configs['rules'].append([description_match, *limits, category_name])
        print('Successful')
    else:
        print('Category does not exist')

    return configs