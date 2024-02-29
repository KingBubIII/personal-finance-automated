import csv

# this function automattically tries to find the relavant columns needed for organizing and totalling
# takes in path to the CSV file and what columns need to be found
def get_row_indexes(path:str, columns: dict[str:int]) -> dict[str:int]:

    with open(path, newline='') as csvfile:
        # get a CSV reader object
        reader = csv.reader(csvfile, 'excel')
        # grabs only the first row which should be the column names
        for row in reader:
            headers = row
            break

        # iterate through each found column name in CSV
        for header_count, header in enumerate(headers):
            # iterate through each passed column name
            for column_name in columns.keys():
                # checks if the columns are similar
                if column_name in header.lower():
                    # sets passed-in column number to the current column number
                    # then exits
                    columns[column_name] = header_count
                    break

    return columns

# build a string the user will see to give the columns an index value
# example:
#      0          1         2
# Post Date, Description, Amount
def show_csv_columns(path):
    # open csv file
    reader = csv.reader(open(path), 'excel')
    # grabs only the first row which should be the column names
    for row in reader:
        headers = row
        break

    col_count_str = ''
    col_names = ''

    for count, header in enumerate(headers):
        col_names += header
        if not count >= len(headers)-1:
            col_names += ', '
        # find middle of header to place header count in center of word(s)
        middle_len = len(header)//2
        # add proper spacing to middle of the header
        # then the column number centered on the header name
        # then add the other half of the spacing
        col_count_str += ' '*middle_len + str(count) + ' '*(len(header)-middle_len+1)

    return col_count_str + '\n' + col_names

def get_data_from_account(file_path, column_indexes):
    reader = csv.reader(open(file_path), 'excel')

    selected_data = []

    for row_index, row in enumerate(reader):
        # skip headers
        if not row_index == 0:
            selected_data.append([row[index] for index in column_indexes])

    return selected_data