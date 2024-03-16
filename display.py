from PySide6.QtWidgets import QComboBox, QVBoxLayout, QWidget, QGridLayout
import classes as cl

def attach_all_tables(accounts_class, display_window):
    for account_name, table_obj in accounts_class.tables.items():
        display_window.layout().addWidget(table_obj, 0, 0)

        # print(type(table_obj))
        table_obj.hide()

def show_table(window_class, accounts_class, table):
    all_account_views = list(accounts_class.tables.values())

    for index in range(window_class.layout().count()):
        obj = window_class.layout().itemAt(index).widget()

        if obj in all_account_views:
            obj.hide()

    table.show()

def start_CSV_review():
    window = QWidget()
    CSV_review_layout = QGridLayout(window)
    # main_layout = QVBoxLayout(main_window)

    # create a object for holding and manipulating CSV data
    all_accounts = cl.Transactions()

    attach_all_tables(all_accounts, window)

    account_selector = QComboBox()
    account_selector.addItems(list(all_accounts.tables.keys()))
    account_selector.currentTextChanged.connect( lambda text: show_table(window, all_accounts, all_accounts.tables[text]) )

    window.layout().addWidget(account_selector, 1, 0)
    account_selector.setCurrentIndex(account_selector.findText("All Accounts"))
    # show_table(main_window, all_accounts, all_accounts.tables["All Accounts"])

    # displays entire window and all objects attached
    window.show()

    return window