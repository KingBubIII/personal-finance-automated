import sys
from PySide6.QtWidgets import QApplication
import classes

# init all nessessary window objects that everything else will attach to
app = QApplication()

window_obj = classes.MainWindow_()

sys.exit(app.exec())