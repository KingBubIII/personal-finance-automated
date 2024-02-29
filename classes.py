import sys
from PySide6 import QtCore, QtWidgets, QtGui

# reads CSV file paths from configs file
# reads all CSV files individually then combines them
class CSVDisplay():
    def __init__(self):

        self.table = self.table_init()

    def table_init(self):
        temp = QtWidgets.QTableWidget()

        temp.setRowCount(3)
        temp.setColumnCount(3)

        for row in range(3):
            for col in range(3):
                item = QtWidgets.QTableWidgetItem(f'Row {row}, Col {col}')
                temp.setItem(row, col, item)

        return temp