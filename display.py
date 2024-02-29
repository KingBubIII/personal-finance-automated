import sys
from PySide6 import QtCore, QtWidgets, QtGui
import classes as cl

if __name__ == "__main__":
    # init all nessessary window objects that everything else will attach to
    app = QtWidgets.QApplication()
    main_window = QtWidgets.QWidget()
    main_layout = QtWidgets.QVBoxLayout(main_window)

    # create a object for holding and manipulating CSV data
    CSV_data = cl.CSVDisplay()

    # adds table to layout so it can be seen
    main_layout.addWidget(CSV_data.tables["ally"])
    # main_layout.removeWidget(CSV_data.tables["ally"])

    # displays entire window and all objects attached
    main_window.show()

    sys.exit(app.exec())