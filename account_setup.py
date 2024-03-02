from easygui import fileopenbox
import csv_ops

from user_input_validation import valid_YN_response, user_confirmed
from configs_ops import update_configs
from classes import AllAccountData

@update_configs
def add_account(configs):
    # asks user input for account identifier and the path the CSV file
    account_name = input('Account nickname: ')
    csv_path = fileopenbox()
    # automatically find columns with names similar to required names
    print(csv_ops.show_csv_columns(csv_path))
    # finds all relavant headers determined by passed class definition
    # passes csv file path and a dictionary of each header with a value of -1
    columnIndexes = csv_ops.get_row_indexes( csv_path,  dict({header:-1} for header in AllAccountData.headers))

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

    configs['categories'][category_name].append([description_match, *limits])

    return configs