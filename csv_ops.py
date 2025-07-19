import csv


def get_headers(path):
    # open csv file
    reader = csv.reader(open(path), "excel")
    # grabs only the first row which should be the column names
    for row in reader:
        headers = row
        return row


# this function automattically tries to find the relavant columns needed for organizing and totalling
# takes in path to the CSV file and what columns need to be found
def get_row_indexes(path: str, columns: dict[str:int]) -> dict[str:int]:

    with open(path, newline="") as csvfile:
        # get a CSV reader object
        reader = csv.reader(csvfile, "excel")
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


def get_data_from_account(path, column_indexes):
    reader = csv.reader(open(path), "excel")

    selected_data = []

    for row_index, row in enumerate(reader):
        # skip headers
        if not row_index == 0:
            selected_data.append([row[index] for index in column_indexes])

    return selected_data
