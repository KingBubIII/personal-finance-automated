from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QWidget
from configs_ops import read_configs, get_account_details
from csv_ops import get_data_from_account, get_headers
from account_setup import defaults, add_override, add_account
from wizardsAndForms import add_account_wizard

class MainWindow_(QWidget):
    def __init__(self, transactions_class):
        super().__init__()
        self.show()

        self.setLayout(QStackedLayout())

        self.setMinimumSize(960,540)

        self.transactions_class = transactions_class

        self.init_home_screen()

    def add_view(self, view, index=0):
        self.layout().insertWidget(index, view)
        self.layout().setCurrentWidget(view)

    def _refresh_home_screen(self):
        self.layout().removeWidget(self.layout().widget(0))
        self.transactions_class.refresh()
        self.init_home_screen()

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

        edit_transactions_btn.clicked.connect(lambda ctx: self.transactions_class.CSV_review(self) )
        import_account_btn.clicked.connect(lambda ctx: add_account_wizard(self))

        progress_bar_widgets = []

        for category_name, budget in configs["categories"].items():
            if not category_name == 'Income':
                curr_bar = ExtendedPogressBar(home)
                curr_bar.setActualRange(0, budget)
                curr_bar.setActualValue(self.transactions_class.get_category_total(category_name))

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
                                                budget_review_area.geometry().left()+25,
                                                budget_review_area.geometry().top()+25,
                                            ),
                                            QSize(25,25)
                                            )
            for progress_bar_component in progress_bar_widgets:
                progress_bar_component[0].setGeometry(
                                                        QRect(
                                                            QPoint(
                                                                prev_selector_geometries.left(),
                                                                prev_selector_geometries.bottom()+25
                                                                ),
                                                            QSize(50, 25)
                                                        )
                                                    )
                progress_bar_component[1].setGeometry(
                                                        QRect(
                                                            QPoint(
                                                                progress_bar_component[0].geometry().right() + 25,
                                                                progress_bar_component[0].geometry().top()
                                                                ),
                                                            QPoint(
                                                                budget_review_area.geometry().right()-25,
                                                                progress_bar_component[0].geometry().bottom()
                                                            )
                                                        )
                                                    )
                prev_selector_geometries = progress_bar_component[0].geometry()

        home.resizeEvent = _resize

        self.add_view(home, 0)

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

class ExtendedPogressBar(QProgressBar):
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)

        self.setRange(0, 100)
        self.setValue(0)
        self.actual_min = 0
        self.actual_val = 0
        self.actual_max = 100

    def refresh_display_value(self):
        test = self.actual_val/self.actual_max*100
        self.setValue( min(test, 100) )
        self.setFormat( f"${self.actual_val}/${self.actual_max}" )

    def setActualMax(self, value):
        self.actual_max = value
        self.refresh_display_value()

    def setActualMin(self, value):
        self.actual_min = value
        self.refresh_display_value()

    def setActualRange(self, minimum, maximum):
        self.actual_min = minimum
        self.actual_max = maximum
        self.refresh_display_value()

    def setActualValue(self, value):
        self.actual_val = value
        self.refresh_display_value()

# reads CSV file paths from configs file
# reads all CSV files individually then combines them
class Transactions():
    def __init__(self):
        self.curr_configs = None
        self.headers = None
        self.accounts = None
        self.categories = None
        self.tables = None

        self.refresh()

    def refresh(self):
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

            return round(abs(actual_amonut),2)

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

    def CSV_review(self, window):
        CSV_review = QWidget(window)
        CSV_review_layout = QGridLayout(CSV_review)

        for account_name, table_obj in self.tables.items():
            CSV_review.layout().addWidget(table_obj, 1, 0)

        # drop down menu to allow users to switch between account tables
        account_selector = QComboBox()
        account_selector.addItems(self.tables.keys())
        # show account table when the drop down menu choice is changed
        account_selector.currentTextChanged.connect( lambda text: self.tables[text].raise_() )
        # on init show the first table in the list
        self.tables[account_selector.itemText(0)].raise_()

        CSV_review.layout().addWidget(account_selector, 2, 0)

        # a button to save all manual overrides and close the window
        return_btn = QPushButton("Save and Exit")
        def _save_and_exit():
            self.commit_all_overrides()
            window.layout().removeWidget(CSV_review)

        return_btn.clicked.connect(_save_and_exit)

        CSV_review.layout().addWidget(return_btn, 0, 0)

        window.add_view(CSV_review)