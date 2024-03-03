import sys
from PySide6.QtWidgets import QApplication
import display

# init all nessessary window objects that everything else will attach to
app = QApplication()

main_window = display.start_CSV_review()

sys.exit(app.exec())