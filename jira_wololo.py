import sys

from PySide6 import QtWidgets
from src.main_window import MainWindow

app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')

window = MainWindow()
window.show()

app.exec()