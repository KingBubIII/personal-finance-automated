import sys
from PySide6.QtWidgets import QApplication
import mainControlClasses

# init all nessessary window objects that everything else will attach to
app = QApplication()

all_transactions = mainControlClasses.Transactions()
window_obj = mainControlClasses.MainWindow_(all_transactions)

sys.exit(app.exec())