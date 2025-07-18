from PySide6.QtWidgets import QWidget
from PySide6.QtCharts import (QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis)
from PySide6.QtGui import QPainter, QColor
from configs_ops import read_configs, get_account_details
from csv_ops import get_data_from_account, get_headers
from account_setup import defaults, add_override, add_account
from wizardsAndForms import *
from qt6WidgetExtensions import *
from math import ceil

class MainWindow_(extendedBasicWidget):
    def __init__(self, transactions_class):
        super().__init__()
        self.show()

        self.setLayout(QStackedLayout())

        self.setMinimumSize(1450,900)
        self.showMaximized()

        self.transactions_class = transactions_class

        self.layout().widgetRemoved.connect(self._refresh_current_view)

        self.init_home_screen()

    def add_view(self, view):
        self.layout().addWidget(view)
        self.layout().setCurrentWidget(view)

    def _refresh_current_view(self):
        self.transactions_class.refresh()
        self.layout().currentWidget().refresh()

    def init_home_screen(self):
        default_margin = 26

        # whole window and layout
        home = extendedBasicWidget(self)
        home.setWindowTitle("Home Screen")
        layout = QGridLayout(home)

        # area to select which accounts to view
        account_selection_area = QGroupBox("Account Selection", home)
        stats_area = QGroupBox("Stats", home)
        budget_review_area = QGroupBox("Budget Review", home)
        checkbox_area = extendedBasicWidget(account_selection_area)
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

        edit_categories_btn = QPushButton("Edit Categories", budget_review_area)
        edit_categories_btn.clicked.connect(lambda ctx: edit_categories_form(self))
        edit_rules_btn = QPushButton("Edit Rules", budget_review_area)
        edit_rules_btn.clicked.connect(lambda ctx: all_rules_manager(self))

        progress_bar_widgets = []
        progress_bar_scroll_obj = QScrollArea(budget_review_area)
        progress_bar_area = extendedBasicWidget(home)
        progress_bar_area_layout = QGridLayout(progress_bar_area)
        progress_bar_scroll_obj.setWidget(progress_bar_area)

        def _create_budget_progress_bars_area():
            for progress_bar in progress_bar_widgets:
                progress_bar.hide()
                progress_bar_area.layout().removeWidget(progress_bar)
            progress_bar_widgets.clear()
            for category_name, budget in read_configs()["categories"].items():
                if not category_name == 'Income':
                    curr_bar = ExtendedPogressBar(progress_bar_area, category_name)
                    curr_bar.setActualRange(0, budget)
                    curr_bar.setActualValue(self.transactions_class.get_category_total(category_name))

                    progress_bar_widgets.append(curr_bar)
        _create_budget_progress_bars_area()


        starting_balance_label = QLabel("Starting Balance: ", stats_area)
        starting_balance_val = QDoubleSpinBox(stats_area)
        starting_balance_val.setDecimals(2)
        starting_balance_val.setMinimum(0.00)
        starting_balance_val.setMaximum(9999999999.00)
        starting_balance_val.setPrefix("$")
        # starting_balance_val.setButtonSymbols(QAbstractSpinBox.NoButtons)
        starting_balance_val.setValue(read_configs()['starting_balance'])
        starting_balance_val.setKeyboardTracking(False)

        ending_balance_label = QLabel("Ending Balance: ", stats_area)
        ending_balance_val = QDoubleSpinBox(stats_area)
        ending_balance_val.setDecimals(2)
        ending_balance_val.setMinimum(0.00)
        ending_balance_val.setMaximum(9999999999.00)
        ending_balance_val.setPrefix("$")
        ending_balance_val.setEnabled(False)

        planned_expenses = QBarSet("Planned")
        planned_expenses.append([self.transactions_class.expenses["planned"], self.transactions_class.income["planned"]])
        planned_expenses.setLabelColor(QColor("black"))
        actual_expenses = QBarSet("Actual")
        actual_expenses.append([self.transactions_class.expenses["actual"], self.transactions_class.income["actual"]])
        actual_expenses.setLabelColor(QColor("black"))

        expense_series = QBarSeries()
        expense_series.setLabelsVisible(True)
        expense_series.setLabelsAngle(-45)

        expense_series.append(planned_expenses)
        expense_series.append(actual_expenses)

        # Set up chart
        chart = QChart()
        chart.addSeries(expense_series)
        chart.setTitle("Planned Vs Actual")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        categories = ["Expenses", "Income"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        axisY = QValueAxis()
        vals = [
                    self.transactions_class.expenses["planned"],
                    self.transactions_class.expenses["actual"],
                    self.transactions_class.income["planned"],
                    self.transactions_class.income["actual"]
                ]
        print(vals)
        axisY.setRange(0, (ceil(int(max(vals)) / 1000) * 1000))

        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
        expense_series.attachAxis(axisX)

        # Chart view
        expenses_chart = QChartView(chart, stats_area)
        expenses_chart.setRenderHint(QPainter.Antialiasing)

        expenses_chart.show()

        @update_configs
        def _update_starting_balance(configs):
            print(starting_balance_val.value())
            configs["starting_balance"] = starting_balance_val.value()
            return configs

        starting_balance_val.valueChanged.connect(lambda ctx: _update_starting_balance())

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

            edit_categories_btn.setGeometry(
                                            QRect(
                                                    QPoint(26,26),
                                                    QSize( budget_review_area.geometry().width()//2-(26*1.5), 26 )
                                            )
                                        )

            edit_rules_btn.setGeometry(
                                        QRect(
                                                QPoint(
                                                        edit_categories_btn.geometry().right()+26,
                                                        edit_categories_btn.geometry().top()
                                                    ),
                                                edit_categories_btn.geometry().size()
                                        )
                                    )

            progress_bar_scroll_obj.setGeometry(
                                                QRect(
                                                    QPoint(
                                                            26,
                                                            edit_categories_btn.geometry().bottom()+26
                                                        ),
                                                    QPoint(
                                                            budget_review_area.geometry().width()-26,
                                                            budget_review_area.geometry().height()-26
                                                        )
                                                    )
                                                )
            progress_bar_area.setGeometry(
                                            QRect(
                                                QPoint(0,0),
                                                QSize(
                                                        progress_bar_scroll_obj.width()-26,
                                                        26*2*len(progress_bar_widgets)-26
                                                    )
                                                )
                                        )

            prev_selector_geometries =  QRect(
                                            QPoint(0,-26),
                                            QSize(0,0)
                                        )
            for progress_bar in progress_bar_widgets:
                progress_bar.setGeometry(
                                        QRect(
                                            QPoint(
                                                prev_selector_geometries.left(),
                                                prev_selector_geometries.bottom()+26
                                                ),
                                            QSize(budget_review_area.width()-52, 26)
                                        )
                                    )
                prev_selector_geometries = progress_bar.geometry()
                progress_bar.show()

            starting_balance_label.setGeometry(QRect(
                                                QPoint(
                                                    default_margin,
                                                    default_margin
                                                    ),
                                                QSize(
                                                        starting_balance_label.sizeHint().width(),
                                                        default_margin
                                                        )
                                                    )
                                            )

            starting_balance_val.setGeometry(QRect(
                                                QPoint(
                                                    starting_balance_label.geometry().right(),
                                                    default_margin
                                                    ),
                                                QSize(
                                                        150,
                                                        default_margin
                                                        )
                                                    )
                                            )
            ending_balance_label.setGeometry(QRect(
                                                QPoint(
                                                    default_margin,
                                                    starting_balance_label.geometry().bottom()+default_margin
                                                    ),
                                                QSize(
                                                        ending_balance_label.sizeHint().width(),
                                                        default_margin
                                                        )
                                                    )
                                            )

            ending_balance_val.setGeometry(QRect(
                                                QPoint(
                                                    ending_balance_label.geometry().right(),
                                                    ending_balance_label.geometry().top(),
                                                    ),
                                                QSize(
                                                        150,
                                                        default_margin
                                                        )
                                                    )
                                            )

            expenses_chart.setGeometry(QRect(
                                            QPoint(
                                                starting_balance_val.geometry().right()+default_margin,
                                                default_margin
                                                ),
                                            QPoint(
                                                stats_area.geometry().width()-default_margin,
                                                stats_area.geometry().height()-default_margin
                                            )
                                            )
                                        )

        home.resizeEvent = _resize

        def _refresh():
            _create_budget_progress_bars_area()
            _resize(None)

        home.refresh = _refresh

        self.add_view(home)

# reads CSV file paths from configs file
# reads all CSV files individually then combines them
class Transactions():
    def __init__(self):
        self.curr_configs = None
        self.headers = None
        self.accounts = None
        self.categories = None
        self.tables = None
        self.expenses = {"planned":0, "actual":0}
        self.income = {"planned":0, "actual":0}

        self.refresh()

    def refresh(self):
        self.curr_configs = read_configs()
        self.headers = defaults(headers=True)
        self.accounts = self.curr_configs["accounts"]
        self.categories = self.curr_configs["categories"]
        self.tables = self.get_all_account_tables()
        self.get_expenses()

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

    def get_expenses(self):
        expense_categories = self.categories.copy()
        del expense_categories["Income"]
        for category in expense_categories:
            self.expenses["actual"] += self.get_category_total(category)
            self.expenses["planned"] += self.categories[category]

    def auto_category(self, transaction):
        # reads in user defined rules from configs file
        all_rules = read_configs()['rules']
        # gets all the string matching rules except for the default 'Misc' category's string match ''
        # all_string_matches = [rule[0] for rule in all_rules[1::]]

        rule_match = False
        rule_index = 1

        # repeat until rule match found or out of categories
        while not rule_match and rule_index<=len(all_rules)-1:
            # curr_string = all_string_matches[curr_string_index]

            if all_rules[rule_index][0] in transaction[2]:
                amt = float(transaction[1])
                if amt > all_rules[rule_index][1] and amt <= all_rules[rule_index][2]:
                    # checks if transaction is under 'income' category
                    if rule_index == 1:
                        # adds income amount to keep track easier
                        self.income["actual"] += amt
                    return all_rules[rule_index][3]
            rule_index+=1

        # defaults to 'misc' category
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
        CSV_review = extendedBasicWidget(window)
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