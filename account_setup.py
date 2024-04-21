import csv_ops
from os import remove

from user_input_validation import valid_YN_response, user_confirmed
from configs_ops import update_configs

def defaults(headers=False, rules=False) -> list[str]:
    if headers:
        return ['date', 'amount', 'description']
    elif rules:
        return ['Misc']

@update_configs
def add_account(configs, account_name, file_path, user_defined_indexes):
    configs['accounts'][account_name] = {"csv_path": file_path, "columnIndexes": user_defined_indexes, "overrides":{}}

    return configs

@update_configs
def add_category(configs):
    # get user input for the name of the rule
    category_name = input("Name your category: ")
    # adds the rule with 3 blanks in a list for the description match, lower limit, upper limit
    configs["categories"].update({category_name:0})

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

@update_configs
def add_override(configs, account_name, row, category):
    # converting row to a string type because json does not handle integers as keys

    # checks that override in that table and row don't exsist
    try:
        configs['accounts'][account_name]['overrides'][str(row)]
        configs['accounts'][account_name]['overrides'][str(row)] = category
    # if it does exsist then overwrite it
    except KeyError as e:
        configs['accounts'][account_name]['overrides'].update({str(row):category})

    return configs

add_category()