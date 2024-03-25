from PySide6.QtWidgets import *
from PySide6.QtCore import *
import classes as cl
from configs_ops import read_configs

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

def configs_setup_GUI():
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

    # for count in range(10):
    #     test = QCheckBox(str(count), checkbox_area)
    #     test.setGeometry(default_margin, default_margin*count, 150, default_margin)
    #     account_check_boxes.append(test)

    import_account_btn = QPushButton('Import Account CSV', account_selection_area)
    edit_transactions_btn = QPushButton('Edit Transactions', account_selection_area)

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
    # window.showMaximized()
    # print(window.geometry().bottom())
    # print(stats_area.geometry().bottom())
    window.show()

    return window
