from PySide6.QtCore import *
from PySide6.QtWidgets import *
from configs_ops import read_configs, get_account_details
from csv_ops import get_data_from_account, get_headers
from account_setup import defaults, add_override, add_account

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

    def _add_view(self, view, index=None):
        if index is None:
            self.layout().addWidget(view)
            self.layout().setCurrentWidget(view)
        else:
            self.layout().insertWidget(0, view)

    def _refresh_home_screen(self):
        self.layout().removeWidget(self.layout().widget(0))
        self.init_home_screen()

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

        configs = read_configs()

        # making it scrollable for when there is many accounts
        scroll_obj = QScrollArea(account_selection_area)
        scroll_obj.setWidget(checkbox_area)

        account_check_boxes = []

        for count, account in enumerate(configs["accounts"]):
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

        progress_bar_widgets = []

        for category_name, budget in configs["categories"].items():
            if not category_name == 'Income':
                curr_bar = QProgressBar(home)
                curr_bar.setMinimum(0)
                curr_bar.setMaximum(budget)
                curr_bar.setValue(Transactions().get_category_total(category_name))

                bar_title = QLabel(category_name,home)

                progress_bar_widgets.append([bar_title, curr_bar])

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

            prev_selector_geometries =  QRect(
                                            QPoint(
                                                budget_review_area.geometry().left()+self.default_widget_margin,
                                                budget_review_area.geometry().top()+self.default_widget_margin,
                                            ),
                                            QSize(25,25)
                                            )
            for progress_bar_component in progress_bar_widgets:
                progress_bar_component[0].setGeometry(
                                                        QRect(
                                                            QPoint(
                                                                prev_selector_geometries.left(),
                                                                prev_selector_geometries.bottom()+self.default_widget_margin
                                                                ),
                                                            QSize(50, 25)
                                                        )
                                                    )
                progress_bar_component[1].setGeometry(
                                                        QRect(
                                                            QPoint(
                                                                progress_bar_component[0].geometry().right() + self.default_widget_margin,
                                                                progress_bar_component[0].geometry().top()
                                                                ),
                                                            QPoint(
                                                                budget_review_area.geometry().right()-self.default_widget_margin,
                                                                progress_bar_component[0].geometry().bottom()
                                                            )
                                                        )
                                                    )
                prev_selector_geometries = progress_bar_component[0].geometry()

        home.resizeEvent = _resize

        self._add_view(home, 0)

    def add_account_wizard(self):
        account_importing = QWidget(self)
        add_account_layout = QGridLayout(account_importing)

        close_btn = QPushButton("close", account_importing)
        import_CSV_btn = QPushButton("Import CSV", account_importing)
        file_dialog = QFileDialog(account_importing)
        headers_selection_table = QTableWidget(1, 0, account_importing)
        account_name_editor = QTextEdit(account_importing)
        account_name_label = QLabel("Account name: ", account_importing)

        headers = defaults(headers=True)
        headers_selectors = QButtonGroup(account_importing)
        for index, header in enumerate(headers):
            temp_btn = QRadioButton(header, account_importing)
            temp_btn.setDisabled(True)
            headers_selectors.addButton(temp_btn)
            headers_selectors.setId(temp_btn, index)

        next_header_btn = QPushButton("Next", account_importing)
        prev_header_btn = QPushButton("Previous", account_importing)
        directions_box = QLabel("Import a CSV file",account_importing)
        finish_btn = QPushButton("Finish", account_importing)

        header_indexes = {header:-1 for header in headers}

        directions_box.setAlignment(Qt.AlignCenter)
        prev_header_btn.setDisabled(True)
        next_header_btn.setDisabled(True)

        def _show_headers():
            file_dialog.exec()

            headers = get_headers(file_dialog.selectedFiles()[0])

            headers_selection_table.setColumnCount(len(headers))

            for index in range(len(headers)):
                headers_selection_table.setItem(0, index, QTableWidgetItem(headers[index]))

            next_header_btn.setDisabled(False)

            for header_radio_btn in headers_selectors.buttons():
                header_radio_btn.setDisabled(False)
            headers_selectors.buttons()[0].click()

        import_CSV_btn.clicked.connect(_show_headers)

        def _btn_disabler():
            selected_header_btn = headers_selectors.checkedButton()
            header_selected_id = headers_selectors.id(selected_header_btn)

            prev_header_btn.setDisabled(False)
            next_header_btn.setDisabled(False)

            if header_selected_id >= len(headers_selectors.buttons())-1:
                next_header_btn.setDisabled(True)

            if header_selected_id == 0:
                prev_header_btn.setDisabled(True)

        def _select_header(prev=False, next=False):
            selected_cells = headers_selection_table.selectedItems()
            if len(selected_cells) == 0:
                print("You have not selected any cell. Try again")
                return
            elif len(selected_cells) > 1:
                print("You have selected too many cells. Just select one for this header")
                return

            selected_header_btn = headers_selectors.checkedButton()
            header_indexes[selected_header_btn.text()] = selected_cells[0].column()

            header_selected_id = headers_selectors.id(selected_header_btn)

            if next:
                headers_selectors.button(header_selected_id+1).click()

            if prev:
                headers_selectors.button(header_selected_id-1).click()

            _btn_disabler()

        next_header_btn.clicked.connect(lambda ctx: _select_header(next=True))
        prev_header_btn.clicked.connect(lambda ctx: _select_header(prev=True))
        headers_selection_table.cellClicked.connect(lambda ctx: _select_header())

        def _radio_btn_click_handler(btn):
            headers_selection_table.clearSelection()
            user_selected_column = header_indexes[btn.text()]
            if not user_selected_column == -1:
                item = headers_selection_table.item(0, user_selected_column)
                headers_selection_table.setCurrentItem(item)

            _btn_disabler()

        headers_selectors.buttonClicked.connect(_radio_btn_click_handler)

        def _exit_wizard():
            self.layout().removeWidget(account_importing)

        close_btn.clicked.connect(_exit_wizard)

        def _save_new_account():
            for header, index in header_indexes.items():
                if index < 0:
                    print("You have not selected columns for all nessessary headers")
                    return
            if get_account_details(account_name_editor.toPlainText()):
                print("An account with that name already exists, give this account a new name")
                return
            if account_name_editor.toPlainText() == "":
                print("Give your acconut a name")
                return

            add_account(account_name_editor.toPlainText(), file_dialog.selectedFiles()[0], header_indexes)
            account_name_editor.clear()
            headers_selection_table.clear()
            self._refresh_home_screen()
            return

        finish_btn.clicked.connect(_save_new_account)

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
            account_name_label.setGeometry(
                                        QRect(
                                                QPoint(
                                                        self.default_widget_margin,
                                                        import_CSV_btn.geometry().bottom()+self.default_widget_margin

                                                ),
                                                QSize(
                                                    100,
                                                    self.default_widget_margin
                                                )

                                            ),
                                    )
            account_name_editor.setGeometry(
                                        QRect(
                                                QPoint(
                                                        account_name_label.geometry().right(),
                                                        import_CSV_btn.geometry().bottom()+self.default_widget_margin
                                                ),
                                                QSize(
                                                    300,
                                                    self.default_widget_margin
                                                )

                                            ),
                                    )
            headers_selection_table.setGeometry(
                                            QRect(
                                                QPoint(
                                                        self.default_widget_margin,
                                                        account_name_editor.geometry().bottom()+self.default_widget_margin
                                                    ),
                                                QSize(
                                                    self.geometry().width()//2,
                                                    self.default_widget_margin*3
                                                )
                                            )
                                        )

            prev_selector_geometry = QRect(0,0,0,0)
            for index, selector in enumerate(headers_selectors.buttons()):
                selector.setGeometry(
                                        QRect(
                                            QPoint(
                                                    prev_selector_geometry.right()+self.default_widget_margin,
                                                    headers_selection_table.geometry().bottom()+self.default_widget_margin
                                                ),
                                            QSize(
                                                selector.sizeHint().width(),
                                                self.default_widget_margin
                                            )
                                        )
                                    )
                prev_selector_geometry = selector.geometry()
            prev_header_btn.setGeometry(
                                            QRect(
                                                QPoint( self.default_widget_margin,
                                                        headers_selectors.buttons()[0].geometry().bottom()+self.default_widget_margin
                                                        ),
                                                QSize(
                                                    headers_selection_table.geometry().width()//3,
                                                    self.default_widget_margin
                                                )
                                            )
                                        )
            directions_box.setGeometry(
                                        QRect(
                                            QPoint( prev_header_btn.geometry().right(),
                                                    headers_selectors.buttons()[0].geometry().bottom()+self.default_widget_margin
                                                    ),
                                            QSize(
                                                headers_selection_table.geometry().width()//3,
                                                self.default_widget_margin
                                            )
                                        )
                                    )
            next_header_btn.setGeometry(
                                        QRect(
                                            QPoint( directions_box.geometry().right(),
                                                    headers_selectors.buttons()[0].geometry().bottom()+self.default_widget_margin
                                                    ),
                                            QSize(
                                                headers_selection_table.geometry().width()//3,
                                                self.default_widget_margin
                                            )
                                        )
                                    )
            finish_btn.setGeometry(
                                        QRect(
                                            QPoint( directions_box.geometry().left(),
                                                    directions_box.geometry().bottom()+self.default_widget_margin
                                                    ),
                                            directions_box.geometry().size()
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
        self.curr_configs = read_configs()
        self.headers = defaults(headers=True)
        self.accounts = self.curr_configs["accounts"]
        self.categories = self.curr_configs["categories"]
        self.tables = self.get_all_account_tables()

    def get_category_total(self, category_name):
        try:
            category_budget = self.categories[category_name]

            actual_amonut = 0
            for table_name, table in self.tables.items():
                for row_index in range(table.rowCount()):
                    transaction_category = table.item(row_index, table.columnCount()-1).text()
                    if transaction_category == category_name:
                        actual_amonut += float(table.item(row_index, self.headers.index("amount")).text())

            return abs(actual_amonut)

        except KeyError as e:
            print("That category name doesn't exist")
            return None

    def auto_category(self, transaction):
        # reads in user defined rules from configs file
        all_rules = read_configs()['rules']
        # gets all the string matching rules except for the default 'Misc' category's string match ''
        # all_string_matches = [rule[0] for rule in all_rules[1::]]

        rule_match = False
        curr_string_index = 1

        # repeat till
        while not rule_match and curr_string_index<=len(all_rules)-1:
            # curr_string = all_string_matches[curr_string_index]

            if all_rules[curr_string_index][0] in transaction[2]:
                transaction[1] = float(transaction[1])
                if transaction[1] > all_rules[curr_string_index][1] and transaction[1] <= all_rules[curr_string_index][2]:
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