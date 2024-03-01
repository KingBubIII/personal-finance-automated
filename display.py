import sys
from PySide6.QtWidgets import QComboBox, QVBoxLayout, QApplication, QWidget, QWidgetItem, QTableWidget
import classes as cl

def init_all_tables(accounts_class, display_window):
    for account_name, table_obj in accounts_class.tables.items():
        display_window.layout().addWidget(table_obj)

        print(type(table_obj))
        table_obj.hide()

def show_table(window_class, accounts_class, table):
    all_account_views = list(accounts_class.tables.values())

    for index in range(window_class.layout().count()):
        obj = window_class.layout().itemAt(index).widget()

        if obj in all_account_views:
            obj.hide()

    table.show()
    window_class.layout().update()

if __name__ == "__main__":
    # init all nessessary window objects that everything else will attach to
    app = QApplication()
    main_window = QWidget()
    main_layout = QVBoxLayout(main_window)
    # main_layout = QVBoxLayout(main_window)

    # create a object for holding and manipulating CSV data
    all_accounts = cl.AllAccountData()

    init_all_tables(all_accounts, main_window)

    next_table_btn = QComboBox()
    next_table_btn.addItems(list(all_accounts.tables.keys()))
    next_table_btn.currentTextChanged.connect( lambda text: show_table(main_window, all_accounts, all_accounts.tables[text]) )

    main_window.layout().addWidget(next_table_btn)

    # displays entire window and all objects attached
    main_window.show()

    sys.exit(app.exec())