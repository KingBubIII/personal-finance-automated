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
        
        # build a string the user will see 
        # user will determine if the automatically found headers are matching correctly with the passed headers
        # example:
        #      0          1         2
        # Post Date, Description, Amount
        
        all_headers_joined = ', '.join(headers)
        user_view = [list(' '*len(all_headers_joined)), all_headers_joined]
        # var to track current char index
        prev_index = 0
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
            
            # find the middle of the CSV file header
            middle_len = len(header)//2
            # get index of character where CSV header count will go
            prev_index += middle_len
            # set character
            user_view[0][prev_index+2] = str(header_count)
            # add the other half of the word worth of spaces plus the ', ' delimiter
            prev_index += middle_len + 2
            
    return "".join(user_view[0]) + '\n' + user_view[1], columns