from PySide6.QtWidgets import *
from PySide6.QtCore import *
import classes as cl
from configs_ops import read_configs
from account_setup import add_account

def add_account_GUI():
    window = QWidget()
    add_account_layout = QGridLayout(window)

    close_btn = QPushButton("close", window)
    close_btn.setGeometry(25,25,100,100)
    close_btn.clicked.connect(window.close)

    import_CSV_btn = QPushButton("Import CSV", window)
    import_CSV_btn.setGeometry(50,50,200,200)
    window.layout().addWidget(import_CSV_btn)

    headers_selection = QTableWidget(window)
    window.layout().addWidget(headers_selection)

    window.show()
