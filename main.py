import sys
from PySide6.QtWidgets import QApplication
import classes

# init all nessessary window objects that everything else will attach to
app = QApplication()

window_obj = classes.MainWindow_()
window_obj._show_current_screen()

sys.exit(app.exec())