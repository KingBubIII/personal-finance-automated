import sys
from PySide6.QtWidgets import QApplication
import classes

# init all nessessary window objects that everything else will attach to
app = QApplication()

all_transactions = classes.Transactions()
window_obj = classes.MainWindow_(all_transactions)

sys.exit(app.exec())