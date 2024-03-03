from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QGridLayout
from configs_ops import read_configs
from csv_ops import get_data_from_account

# reads CSV file paths from configs file
# reads all CSV files individually then combines them
class AllAccountData():
    def __init__(self):
        self.headers = ['date', 'amount', 'description']
        self.tables = self.read_all_CSV_files()

    def read_all_CSV_files(self):
        # read in all accounts added to configs file
        configs = read_configs()
        tables = {}
        # creates a table to hold all table data together
        all_combined = QTableWidget(0, len(self.headers))
        # sets combined table headers
        all_combined.setHorizontalHeaderLabels(self.headers)

        # loops through all accounts found in confgis file
        for account_name, account_details in configs["accounts"].items():
            # creates blank Qt6 table object with enough columns for each header
            table_obj = QTableWidget(0, len(self.headers))
            # sets headers on table object
            table_obj.setHorizontalHeaderLabels(self.headers)

            # read in account CSV file data
            # pass csv file path and only relevant header indexes
            data = get_data_from_account(account_details['csv_path'],  [account_details['columnIndexes'][temp_header] for temp_header in self.headers] )
            # iterate through each row of CSV data
            for row_index in range(len(data)):
                # add a row to the table object and combined table
                table_obj.insertRow(table_obj.rowCount())
                all_combined.insertRow(all_combined.rowCount())
                # iterate for each column
                for col_index in range(len(self.headers)):
                    # converts CSV data into a table item object for current table and combined table
                    table_obj.setItem(row_index, col_index, QTableWidgetItem(data[row_index][col_index]))
                    all_combined.setItem(all_combined.rowCount()-1, col_index, QTableWidgetItem(data[row_index][col_index]))
            # add the current table to the whole tables dictionary
            tables[account_name] = table_obj

        tables['All Accounts'] = all_combined

        return tables

    def get_account_table(self, account_name):
        # print(account_name)
        return self.tables[account_name]