from PySide6.QtCore import QObject
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QStyledItemDelegate, QComboBox
from configs_ops import read_configs
from csv_ops import get_data_from_account

class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, dropdown_options: list[str]) -> None:
        super().__init__()

        self.dropdown_options = dropdown_options

    def createEditor(self, parent, option, index):
        comboBox = QComboBox(parent)
        comboBox.addItems(self.dropdown_options)
        return comboBox

# reads CSV file paths from configs file
# reads all CSV files individually then combines them
class AllAccountData():
    def __init__(self):
        self.headers = ['date', 'amount', 'description']
        self.categories = list(read_configs()['categories'].keys())
        self.tables = self.get_all_account_tables()

    def get_all_account_tables(self):
        # read in all accounts added to configs file
        configs = read_configs()
        tables = {}
        # creates a table to hold all table data together
        all_combined = QTableWidget(0, len(self.headers)+1)
        # sets combined table headers
        all_combined.setHorizontalHeaderLabels([*self.headers, 'Categories'])

        all_combined.setItemDelegateForColumn(len(self.headers), ComboBoxDelegate(self.categories))
        all_combined.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

        # loops through all accounts found in confgis file
        for account_name, account_details in configs["accounts"].items():
            # creates blank Qt6 table object with enough columns for each header
            table_obj = QTableWidget(0, len(self.headers)+1)
            # sets headers on table object
            table_obj.setHorizontalHeaderLabels([*self.headers, 'Categories'])
            table_obj.setItemDelegateForColumn(len(self.headers), ComboBoxDelegate(self.categories))
            table_obj.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

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