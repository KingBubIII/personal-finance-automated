from PySide6.QtCore import *
from PySide6.QtWidgets import *
from configs_ops import read_configs, get_account_details, update_configs
from csv_ops import get_data_from_account, get_headers
from account_setup import defaults, update_categories, add_account

def add_account_wizard(window):
    account_importing_view = QWidget(window)
    add_account_layout = QGridLayout(account_importing_view)
    default_margin = 26

    close_btn = QPushButton("close", account_importing_view)
    import_CSV_btn = QPushButton("Import CSV", account_importing_view)
    file_dialog = QFileDialog(account_importing_view)
    headers_selection_table = QTableWidget(1, 0, account_importing_view)
    account_name_editor = QTextEdit(account_importing_view)
    account_name_label = QLabel("Account name: ", account_importing_view)

    headers = defaults(headers=True)
    headers_selectors = QButtonGroup(account_importing_view)
    for index, header in enumerate(headers):
        temp_btn = QRadioButton(header, account_importing_view)
        temp_btn.setDisabled(True)
        headers_selectors.addButton(temp_btn)
        headers_selectors.setId(temp_btn, index)

    next_header_btn = QPushButton("Next", account_importing_view)
    prev_header_btn = QPushButton("Previous", account_importing_view)
    directions_box = QLabel("Import a CSV file",account_importing_view)
    finish_btn = QPushButton("Finish", account_importing_view)

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
        window.layout().removeWidget(account_importing_view)

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
        window._refresh_home_screen()
        return

    finish_btn.clicked.connect(_save_new_account)

    def _resize(ctx=None):
        close_btn.setGeometry(
                                QRect(
                                        QPoint( default_margin,
                                                default_margin
                                                ),
                                        QSize(  100,
                                                default_margin
                                            )
                                    )
                            )
        import_CSV_btn.setGeometry(
                                    QRect(
                                            QPoint(
                                                    default_margin,
                                                    close_btn.geometry().bottom()+100

                                            ),
                                            QSize(
                                                100,
                                                default_margin
                                            )

                                        ),
                                )
        account_name_label.setGeometry(
                                    QRect(
                                            QPoint(
                                                    default_margin,
                                                    import_CSV_btn.geometry().bottom()+default_margin

                                            ),
                                            QSize(
                                                100,
                                                default_margin
                                            )

                                        ),
                                )
        account_name_editor.setGeometry(
                                    QRect(
                                            QPoint(
                                                    account_name_label.geometry().right(),
                                                    import_CSV_btn.geometry().bottom()+default_margin
                                            ),
                                            QSize(
                                                300,
                                                default_margin
                                            )

                                        ),
                                )
        headers_selection_table.setGeometry(
                                        QRect(
                                            QPoint(
                                                    default_margin,
                                                    account_name_editor.geometry().bottom()+default_margin
                                                ),
                                            QSize(
                                                window.geometry().width()//2,
                                                default_margin*3
                                            )
                                        )
                                    )

        prev_selector_geometry = QRect(0,0,0,0)
        for index, selector in enumerate(headers_selectors.buttons()):
            selector.setGeometry(
                                    QRect(
                                        QPoint(
                                                prev_selector_geometry.right()+default_margin,
                                                headers_selection_table.geometry().bottom()+default_margin
                                            ),
                                        QSize(
                                            selector.sizeHint().width(),
                                            default_margin
                                        )
                                    )
                                )
            prev_selector_geometry = selector.geometry()
        prev_header_btn.setGeometry(
                                        QRect(
                                            QPoint( default_margin,
                                                    headers_selectors.buttons()[0].geometry().bottom()+default_margin
                                                    ),
                                            QSize(
                                                headers_selection_table.geometry().width()//3,
                                                default_margin
                                            )
                                        )
                                    )
        directions_box.setGeometry(
                                    QRect(
                                        QPoint( prev_header_btn.geometry().right(),
                                                headers_selectors.buttons()[0].geometry().bottom()+default_margin
                                                ),
                                        QSize(
                                            headers_selection_table.geometry().width()//3,
                                            default_margin
                                        )
                                    )
                                )
        next_header_btn.setGeometry(
                                    QRect(
                                        QPoint( directions_box.geometry().right(),
                                                headers_selectors.buttons()[0].geometry().bottom()+default_margin
                                                ),
                                        QSize(
                                            headers_selection_table.geometry().width()//3,
                                            default_margin
                                        )
                                    )
                                )
        finish_btn.setGeometry(
                                    QRect(
                                        QPoint( directions_box.geometry().left(),
                                                directions_box.geometry().bottom()+default_margin
                                                ),
                                        directions_box.geometry().size()
                                    )
                                )

    # _resize()
    account_importing_view.resizeEvent = _resize

    window.add_view(account_importing_view)

def edit_categories_form(window):
    edit_categories_view = QWidget(window)
    layout = QGridLayout(edit_categories_view)

    save_exit_btn = QPushButton("Save and Exit", edit_categories_view)

    configs = read_configs()

    all_category_objs = []
    for category_name, category_budget in configs["categories"].items():
        if not category_name == "Income":
            curr_category_name_obj = QTextEdit(category_name, edit_categories_view)
            if category_name == "Misc":
                curr_category_name_obj.setDisabled(True)
            curr_category_budget_obj = QTextEdit(str(category_budget), edit_categories_view)

            all_category_objs.append([curr_category_name_obj, curr_category_budget_obj])

    def _save_and_exit():
        categories_dict = {}
        for objs in all_category_objs:
            categories_dict.update( {objs[0].toPlainText():int(objs[1].toPlainText())} )

        update_categories(categories_dict)

        window.layout().removeWidget(edit_categories_view)

        return configs
    save_exit_btn.clicked.connect(lambda ctx: _save_and_exit())

    def _resize():
        save_exit_btn.setGeometry(
                                    QRect(
                                            QPoint(26, 26),
                                            QSize(100, 26)
                                        )
                                    )

        prev_obj = save_exit_btn
        for category_obj in all_category_objs:
            category_obj[0].setGeometry(
                                        QRect(
                                                QPoint(26, prev_obj.geometry().bottom()+26),
                                                QSize(100, 26 )
                                            )
                                        )
            category_obj[1].setGeometry(
                                        QRect(
                                                QPoint(category_obj[0].geometry().right()+26, prev_obj.geometry().bottom()+26),
                                                QSize(100, 26)
                                            )
                                        )
            prev_obj = category_obj[0]

    _resize()

    window.add_view(edit_categories_view)