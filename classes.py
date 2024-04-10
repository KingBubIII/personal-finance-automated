from PySide6.QtCore import *
from PySide6.QtWidgets import *
from configs_ops import read_configs
from csv_ops import get_data_from_account, get_headers
from account_setup import defaults, add_override

class MainWindow_(QWidget):
    def __init__(self):
        super().__init__()
        self.show()

        self.setLayout(QStackedLayout())

        self.setMinimumSize(960,540)
        self.default_widget_margin = 25

        self.init_home_screen()

    def _attach_all_tables(self, accounts_class, display_window):
        for account_name, table_obj in accounts_class.tables.items():
            display_window.layout().addWidget(table_obj, 1, 0)

    def _show_table(self, window_class, table):
        table.raise_()

    def _add_view(self, view):
        self.layout().addWidget(view)
        self.layout().setCurrentWidget(view)

    def start_CSV_review(self, selected_tables):
        CSV_review = QWidget(self)
        CSV_review_layout = QGridLayout(CSV_review)

        # create a object for holding and manipulating CSV data
        all_accounts = Transactions()

        self._attach_all_tables(all_accounts, CSV_review)

        # drop down menu to allow users to switch between account tables
        account_selector = QComboBox()
        account_selector.addItems(selected_tables)
        # show account table when the drop down menu choice is changed
        account_selector.currentTextChanged.connect( lambda text: self._show_table(CSV_review, all_accounts.tables[text]) )
        # on init show the first table in the list
        self._show_table(CSV_review, all_accounts.tables[account_selector.itemText(0)])

        CSV_review.layout().addWidget(account_selector, 2, 0)

        # a button to save all manual overrides and close the window
        return_btn = QPushButton("Save and Exit")
        def _save_and_exit():
            all_accounts.commit_all_overrides()
            self.layout().removeWidget(CSV_review)

        return_btn.clicked.connect(_save_and_exit)

        CSV_review.layout().addWidget(return_btn, 0, 0)

        self._add_view(CSV_review)

    def init_home_screen(self):
        default_margin = 25

        # whole window and layout
        home = QWidget(self)
        layout = QGridLayout(home)

        # area to select which accounts to view
        account_selection_area = QGroupBox("Account Selection", home)
        stats_area = QGroupBox("Stats", home)
        budget_review_area = QGroupBox("Budget Review", home)
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
        import_account_btn.clicked.connect(lambda ctx: self.add_account_wizard())

        def _resize(event):
            account_selection_area.setGeometry( default_margin,
                                                default_margin,
                                                home.geometry().width()//2,
                                                home.geometry().height()//3)

            stats_area.setGeometry(QRect(
                                        QPoint(
                                                default_margin,
                                                account_selection_area.geometry().bottom()+default_margin
                                                ),
                                        QPoint(
                                                account_selection_area.geometry().right(),
                                                home.geometry().bottom()-default_margin
                                                )
                                        )
                                    )

            budget_review_area.setGeometry(QRect(
                                        QPoint(
                                                account_selection_area.geometry().right()+default_margin,
                                                default_margin
                                                ),
                                        QPoint(
                                                home.geometry().right()-default_margin,
                                                home.geometry().bottom()-default_margin
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

        home.resizeEvent = _resize

        self._add_view(home)

    def add_account_wizard(self):
        account_importing = QWidget(self)
        add_account_layout = QGridLayout(account_importing)

        close_btn = QPushButton("close", account_importing)
        import_CSV_btn = QPushButton("Import CSV", account_importing)
        file_dialog = QFileDialog(account_importing)
        headers_selection = QTableWidget(1, 0, account_importing)
        next_header_btn = QPushButton("Next", account_importing)
        prev_header_btn = QPushButton("Previous", account_importing)
        directions_box = QLabel("Select the date column",account_importing)

        directions_box.setAlignment(Qt.AlignCenter)

        def _show_headers():
            file_dialog.exec()

            headers = get_headers(file_dialog.selectedFiles()[0])

            headers_selection.setColumnCount(len(headers))

            for index in range(len(headers)):
                headers_selection.setItem(0, index, QTableWidgetItem(headers[index]))

        import_CSV_btn.clicked.connect(_show_headers)


        def _resize(ctx=None):
            close_btn.setGeometry(
                                    QRect(
                                            QPoint( self.default_widget_margin,
                                                    self.default_widget_margin
                                                    ),
                                            QSize(  100,
                                                    self.default_widget_margin
                                                )
                                        )
                                )
            import_CSV_btn.setGeometry(
                                        QRect(
                                                QPoint(
                                                        self.default_widget_margin,
                                                        close_btn.geometry().bottom()+100

                                                ),
                                                QSize(
                                                    100,
                                                    self.default_widget_margin
                                                )

                                            ),
                                    )
            headers_selection.setGeometry(
                                            QRect(
                                                QPoint(
                                                        self.default_widget_margin,
                                                        import_CSV_btn.geometry().bottom()+self.default_widget_margin
                                                    ),
                                                QSize(
                                                    self.geometry().width()//2,
                                                    self.default_widget_margin*3
                                                )
                                            )
                                        )
            prev_header_btn.setGeometry(
                                            QRect(
                                                QPoint( self.default_widget_margin,
                                                        headers_selection.geometry().bottom()+self.default_widget_margin
                                                        ),
                                                QSize(
                                                    headers_selection.geometry().width()//3,
                                                    self.default_widget_margin
                                                )
                                            )
                                        )
            directions_box.setGeometry(
                                        QRect(
                                            QPoint( prev_header_btn.geometry().right(),
                                                    headers_selection.geometry().bottom()+self.default_widget_margin
                                                    ),
                                            QSize(
                                                headers_selection.geometry().width()//3,
                                                self.default_widget_margin
                                            )
                                        )
                                    )
            next_header_btn.setGeometry(
                                        QRect(
                                            QPoint( directions_box.geometry().right(),
                                                    headers_selection.geometry().bottom()+self.default_widget_margin
                                                    ),
                                            QSize(
                                                headers_selection.geometry().width()//3,
                                                self.default_widget_margin
                                            )
                                        )
                                    )


        _resize()
        account_importing.resizeEvent = _resize

        self._add_view(account_importing)

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