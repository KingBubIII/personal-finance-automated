from PySide6 import QtCore, QtWidgets, QtGui
from configs_ops import read_configs
from csv_ops import get_data_from_account

# reads CSV file paths from configs file
# reads all CSV files individually then combines them
class CSVDisplay():
    def __init__(self):

        self.tables = self.read_all_CSV_files()

    def read_all_CSV_files(self):
        configs = read_configs()
        tables = {}


        for account_name, account_details in configs["accounts"].items():
            headers = list(account_details['columnIndexes'].keys())

            table_obj = QtWidgets.QTableWidget(0, len(headers))

            table_obj.setHorizontalHeaderLabels(headers)

            data = get_data_from_account(account_details['csv_path'], list(account_details['columnIndexes'].values()) )
            for row_index in range(len(data)):
                for col_index in range(len(data[row_index])):
                    table_obj.insertRow(table_obj.rowCount())
                    table_obj.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(data[row_index][col_index]))

            tables[account_name] = table_obj

        return tables