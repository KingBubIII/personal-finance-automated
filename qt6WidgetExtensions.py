from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtWidgets import QWidget, QStyledItemDelegate, QComboBox, QTableWidget, QProgressBar, QLabel
from PySide6.QtCharts import QBarSet, QBarSeries, QChart, QBarCategoryAxis, QValueAxis, QChartView
from PySide6.QtGui import QColor
from account_setup import defaults, add_override, add_account
from math import ceil

class CustomChartClass():
    def __init__(self):
        self.planned = QBarSet("Planned")
        self.actual = QBarSet("Actual")
        self.expense_series = QBarSeries()
        self.chart_widget = QChart()

        self.planned.setLabelColor(QColor("black"))
        self.actual.setLabelColor(QColor("black"))

        self.expense_series.setLabelsVisible(True)
        self.expense_series.setLabelsAngle(-45)
        self.expense_series.append(self.planned)
        self.expense_series.append(self.actual)

        self.chart_widget.addSeries(self.expense_series)
        self.chart_widget.setTitle("Planned Vs Actual")
        self.chart_widget.setAnimationOptions(QChart.SeriesAnimations)

        categories = ["Expenses", "Income"]
        self.axisX = QBarCategoryAxis()
        self.axisX.append(categories)

        self.axisY = QValueAxis()
        self.axisY.setRange(0, 0)

        self.chart_widget.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.chart_widget.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.expense_series.attachAxis(self.axisX)
        self.expense_series.attachAxis(self.axisY)

    def refresh_chart(self, expenses: dict, incomes: dict):
        self.planned.remove(0, self.planned.count())
        self.actual.remove(0, self.actual.count())
        
        self.planned.append([expenses["planned"], incomes["planned"]])
        self.actual.append([expenses["actual"], incomes["actual"]])

        expenses_and_incomes = [
                    expenses["planned"],
                    expenses["actual"],
                    incomes["planned"],
                    incomes["actual"]
                ]
        self.axisY.setRange(0, (ceil(int(max(expenses_and_incomes)) / 1000) * 1000))



class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, dropdown_options: list[str]) -> None:
        super().__init__()

        self.dropdown_options = dropdown_options

    def createEditor(self, parent, option, index):
        comboBox = QComboBox(parent)
        comboBox.addItems(self.dropdown_options)
        return comboBox

class ExtendedTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # overrides not allowed by default to not create errors when loading in the CSV files
        self.allow_overrides = False
        self.uncommited_overrides = {}
        self.cellChanged.connect(self.stage_override)

    def stage_override(self):
        # checks to see if overrides are allowed
        if self.allow_overrides:
            self.uncommited_overrides.update({self.currentRow(): self.currentItem().text()})

    # one by one adds the manual override to the proper account in the configs file
    def commit_overrides(self):
        # saves overrides to configs file
        for row, category in self.uncommited_overrides.items():
            add_override(self.objectName(), row, category)

        # empties out all overrides
        self.uncommited_overrides = {}

class ExtendedPogressBar(QProgressBar):
    def __init__(self, parent: QWidget | None, category_name) -> None:
        super().__init__(parent)

        # set display values to 0-100 to represent percentages
        self.setRange(0, 100)
        self.setValue(0)

        # actual values that will be used for calculation purposes
        self.actual_min = 0
        self.actual_val = 0
        self.actual_max = 100

        # identifier and for user viewing
        self.category_name = category_name

        self.bar_description_text = QLabel(self)
        self.bar_description_text.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # update the text shown
        self.bar_description_text.setText(f"{self.category_name}: ${self.actual_val}/${self.actual_max}")
        # update recommended size
        self.bar_description_text.setGeometry(
                                                QRect(
                                                        QPoint(self.bar_description_text.geometry().topLeft()),
                                                        self.bar_description_text.sizeHint()
                                                    )
                                            )
        # move text to center over the progress bar
        self.bar_description_text.move(
                                        (self.width()//2)-(self.bar_description_text.width()//2),
                                        (self.height()//2)-(self.bar_description_text.height()//2)
                                    )

    def refresh_display_value(self):
        if self.actual_max == 0:
            percentage = self.actual_val/1*100
        else:
            percentage = self.actual_val/self.actual_max*100
        self.setValue( min(percentage, 100) )
        self.bar_description_text.setText(f"{self.category_name}: ${self.actual_val}/${self.actual_max}")
        self.setFormat("")

    def setActualMax(self, value):
        self.actual_max = value
        self.refresh_display_value()

    def setActualMin(self, value):
        self.actual_min = value
        self.refresh_display_value()

    def setActualRange(self, minimum, maximum):
        self.actual_min = minimum
        self.actual_max = maximum
        self.refresh_display_value()

    def setActualValue(self, value):
        self.actual_val = value
        self.refresh_display_value()

class extendedBasicWidget(QWidget):
    def __init__(self, parent: QWidget | None = None ) -> None:
        super().__init__(parent)

    def refresh(self):
        print(self)
