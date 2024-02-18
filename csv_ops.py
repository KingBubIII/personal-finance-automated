import csv

def get_row_indexes(path:str, columns: dict[str:int]) -> dict[str:int]:
    with open(path, newline='') as csvfile:
        column_numbers_string = ''
        reader = csv.reader(csvfile, 'excel')
        for row in reader:
            headers = row
            break

        user_view = [list(' '*len(', '.join(headers))), ', '.join(headers)]
        prev_index = 0
        for header_count, header in enumerate(headers):
            for column_name in columns.keys():
                if column_name in header.lower():
                    columns[column_name] = header_count
                    break

            middle_len = len(header)//2
            new_index = prev_index+middle_len
            user_view[0][new_index+2] = str(header_count)
            prev_index = new_index + middle_len +2
            
    return "".join(user_view[0]) + '\n' + user_view[1], columns