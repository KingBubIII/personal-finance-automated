from PySide6.QtCore import *
from PySide6.QtWidgets import *
from configs_ops import read_configs
from csv_ops import get_data_from_account
from account_setup import defaults, add_override

class MainWindow_():
    def __init__(self):
        self.current_screen = None
        self.screen_stack = []

        self.init_home_screen()

    def _show_current_screen(self):
        for window in self.screen_stack:
            window.hide()
        self.current_screen = self.screen_stack[-1]
        self.current_screen.show()

    # new decorator for creating a new screen
    def add_screen(self, new_screen):

        self.screen_stack.append(new_screen)
        self.current_screen = new_screen

        self._show_current_screen()

    def go_back(self):
        if len(self.screen_stack) > 1:
            self.current_screen.close()
            self.screen_stack.pop()

        self._show_current_screen()

    def _attach_all_tables(self, accounts_class, display_window):
        for account_name, table_obj in accounts_class.tables.items():
            display_window.layout().addWidget(table_obj, 1, 0)

    def _show_table(self, window_class, table):
        table.raise_()

    def start_CSV_review(self, selected_tables):
        window = QWidget()
        CSV_review_layout = QGridLayout(window)

        # create a object for holding and manipulating CSV data
        all_accounts = Transactions()

        self._attach_all_tables(all_accounts, window)

        # drop down menu to allow users to switch between account tables
        account_selector = QComboBox()
        account_selector.addItems(selected_tables)
        # show account table when the drop down menu choice is changed
        account_selector.currentTextChanged.connect( lambda text: self._show_table(window, all_accounts.tables[text]) )
        # on init show the first table in the list
        self._show_table(window, all_accounts.tables[account_selector.itemText(0)])

        window.layout().addWidget(account_selector, 2, 0)

        # a button to save all manual overrides and close the window
        return_btn = QPushButton("Save and Exit")
        def _save_and_exit():
            all_accounts.commit_all_overrides()
            self.go_back()

        return_btn.clicked.connect(_save_and_exit)

        window.layout().addWidget(return_btn, 0, 0)

        self.add_screen(window)

    def init_home_screen(self):
        default_margin = 25

        # whole window and layout
        window = QWidget()
        layout = QGridLayout(window)

        # area to select which accounts to view
        account_selection_area = QGroupBox("Account Selection", window)
        stats_area = QGroupBox("Stats", window)
        budget_review_area = QGroupBox("Budget Review", window)
        checkbox_area = QWidget(account_selection_area)
        checkbox_area_layout = QGridLayout(checkbox_area)

        # making it scrollable for when there is many accounts
        scroll_obj = QScrollArea(account_selection_area)
        scroll_obj.setWidget(checkbox_area)

        account_check_boxes = []

        for count, account in enumerate(read_configs()["accounts"]):
            test = QCheckBox(account, checkbox_area)
            test.setGeometry(default_margin, default_margin*count, 150, default_margin)
            account_check_boxes.append(test)

        import_account_btn = QPushButton('Import Account CSV', account_selection_area)

        edit_transactions_btn = QPushButton('Edit Transactions', account_selection_area)

        def get_selected_accounts():
            selected_account_objs = list(filter(lambda account: account.isChecked(), account_check_boxes))
            return [obj.text() for obj in selected_account_objs]

        edit_transactions_btn.clicked.connect(lambda ctx: self.start_CSV_review(get_selected_accounts()) )
        # import_account_btn.clicked.connect(lambda ctx: self.add_account_GUI())

        def _resize(event):
            account_selection_area.setGeometry( default_margin,
                                                default_margin,
                                                window.geometry().width()//2,
                                                window.geometry().height()//3)

            stats_area.setGeometry(QRect(
                                        QPoint(
                                                default_margin,
                                                account_selection_area.geometry().bottom()+default_margin
                                                ),
                                        QPoint(
                                                account_selection_area.geometry().right(),
                                                window.geometry().bottom()-default_margin
                                                )
                                        )
                                    )

            budget_review_area.setGeometry(QRect(
                                        QPoint(
                                                account_selection_area.geometry().right()+default_margin,
                                                default_margin
                                                ),
                                        QPoint(
                                                window.geometry().right()-default_margin,
                                                window.geometry().bottom()-default_margin
                                                )
                                        )
                                    )

            import_account_btn.setGeometry(QRect(
                                            QPoint(
                                                default_margin,
                                                default_margin
                                                ),
                                            QSize(
                                                    150,
                                                    default_margin
                                                    )
                                                )
                                            )

            edit_transactions_btn.setGeometry(QRect(
                                            QPoint(
                                                import_account_btn.geometry().right()+default_margin,
                                                default_margin
                                                ),
                                            QSize(
                                                    150,
                                                    default_margin
                                                    )
                                                )
                                            )

            scroll_obj.setGeometry(QRect(
                                    QPoint(
                                        default_margin,
                                        import_account_btn.geometry().bottom() + default_margin
                                        ),
                                QPoint(
                                        account_selection_area.geometry().width()-default_margin,
                                        account_selection_area.geometry().height()-default_margin
                                        )
                                    )
                                )

            checkbox_area.setGeometry(
                                        default_margin,
                                        default_margin,
                                        scroll_obj.geometry().width()-default_margin,
                                        default_margin*len(account_check_boxes)
                                    )

        window.resizeEvent = _resize

        self.add_screen(window)

class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, dropdown_options: list[str]) -> None:
        super().__init__()

        self.dropdown_options = dropdown_options

    def createEditor(self, parent, option, index):
        comboBox = QComboBox(parent)
        comboBox.addItems(self.dropdown_options)
        return comboBox

class ExtendedTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # overrides not allowed by default to not create errors when loading in the CSV files
        self.allow_overrides = False
        self.uncommited_overrides = {}
        self.cellChanged.connect(self.stage_override)

    def stage_override(self):
        # checks to see if overrides are allowed
        if self.allow_overrides:
            self.uncommited_overrides.update({self.currentRow(): self.currentItem().text()})

    # one by one adds the manual override to the proper account in the configs file
    def commit_overrides(self):
        # saves overrides to configs file
        for row, category in self.uncommited_overrides.items():
            add_override(self.objectName(), row, category)

        # empties out all overrides
        self.uncommited_overrides = {}

# reads CSV file paths from configs file
# reads all CSV files individually then combines them
class Transactions():
    def __init__(self):
        self.headers = defaults(headers=True)
        self.categories = read_configs()["categories"]
        self.tables = self.get_all_account_tables()

    def auto_category(self, data):
        # reads in user defined rules from configs file
        all_rules = read_configs()['rules']
        # gets all the string matching rules except for the default 'Misc' category's string match ''
        # all_string_matches = [rule[0] for rule in all_rules[1::]]

        rule_match = False
        curr_string_index = 1

        # repeat till
        while not rule_match and curr_string_index<=len(all_rules)-1:
            # curr_string = all_string_matches[curr_string_index]

            if all_rules[curr_string_index][0] in data[2]:
                data[1] = float(data[1])
                if data[1] > all_rules[curr_string_index][1] and data[1] <= all_rules[curr_string_index][2]:
                    return all_rules[curr_string_index][3]

            curr_string_index+=1

        return all_rules[0][3]

    def get_all_account_tables(self):
        # read in all accounts added to configs file
        configs = read_configs()
        tables = {}

        # loops through all accounts found in confgis file
        for account_name, account_details in configs["accounts"].items():
            # creates blank Qt6 table object with enough columns for each header
            table_obj = ExtendedTableWidget(0, len(self.headers)+1)
            table_obj.setObjectName(account_name)

            # sets headers on table object
            table_obj.setHorizontalHeaderLabels([*self.headers, 'Categories'])
            table_obj.setItemDelegateForColumn(len(self.headers), ComboBoxDelegate(self.categories))
            table_obj.setEditTriggers(ExtendedTableWidget.EditTrigger.AllEditTriggers)

            # read in account CSV file data
            # pass csv file path and only relevant header indexes
            data = get_data_from_account(account_details['csv_path'],  [account_details['columnIndexes'][temp_header] for temp_header in self.headers] )
            # iterate through each row of CSV data
            for row_index in range(len(data)):
                # add a row to the table object and combined table
                table_obj.insertRow(table_obj.rowCount())
                # iterate for each column
                for col_index in range(len(self.headers)):
                    # converts CSV data into a table item object for current table and combined table
                    table_obj.setItem(row_index, col_index, QTableWidgetItem(data[row_index][col_index]))

                # the final column of the row is auto catorgized based on previously made rules in the configs
                # default option is "Misc"
                table_obj.setItem(row_index, len(self.headers), QTableWidgetItem(self.auto_category(data[row_index])))

            # loads all overrides user previously made
            for row, category in configs["accounts"][account_name]["overrides"].items():
                table_obj.setItem(int(row), len(self.headers), QTableWidgetItem(category))

            # add the current table to the whole tables dictionary
            tables[account_name] = table_obj

        # enable manual overrides for each table
        for account_name, table_obj in tables.items():
            table_obj.allow_overrides = True

        return tables

    def get_account_table(self, account_name):
        # print(account_name)
        return self.tables[account_name]

    def commit_all_overrides(self):
        for table_name, table_obj in self.tables.items():
            table_obj.commit_overrides()