from os import remove
from json import load, dumps
from easygui import fileopenbox
import csv_ops

def good_input_response(answer):
    answer = answer.upper()
    if answer == "YES" or answer == "Y" or answer == "NO" or answer == "N":
        return True
    else:
        return False

def add_account():
    # loads configs in python hash table
    configs = load(open('configs.json','r'))

    # opens configs file in "write" mode to empty configs file for overwritting later
    with open('configs.json', 'w') as configs_file:
        # asks user input for account identifier and the path the CSV file
        account_name = input('Account nickname: ')
        csv_path = fileopenbox()
        # automatically find columns with names similar to required names
        view_cols, columnIndexes = csv_ops.get_row_indexes(csv_path, {'date': -1, 'amount': -1, 'description': -1})
        
        # iterate though all column, index pairs
        for col_name, col_num in columnIndexes.items():
            print(view_cols)
            response = ''
            # ask user for input until input is valid
            while not good_input_response(response):
                print(col_name, col_num)
                response = input('Is {0} the correct column index for {1}?'.format(col_num, col_name))
            
            if response == "YES" or response == "Y":
                continue
            else:
                while not response.isnumeric():
                    response = input('What column should it be for {0}'.format(col_name))
                
                columnIndexes[col_name] = int(response)

        # adds newly created account details to configs "accounts" section
        configs["accounts"][account_name] = {"csv_path": csv_path, "columnIndexes": columnIndexes}

        # rewrites configs with updated "accounts" info back to file
        configs_file.write(dumps(configs, sort_keys=True, indent=4))

def create_configs():
    # checks if file exists already
    try:
        default_configs = {"accounts": {}}
        with open('configs.json','x') as configs_file:
            configs_file.write(dumps(default_configs, sort_keys=True, indent=4))
    except FileExistsError:
        # get user input if file should be overwritten with default configs
        user_response = input('File already exists, would you like to start fresh? Y/N\n')
        good_response = good_input_response(user_response)
        if good_response:
            if user_response == "YES" or user_response == "Y":
                remove('configs.json')
                # recursively call function to create defaults now that original file is deleted
                create_configs()
            elif user_response == "NO" or user_response == "N":
                print('Cancelled')
        else:
            # recursively call function to get user input agin if configs should be deleted
            print('Not a valid answer\n')
            create_configs()


create_configs()
add_account()