from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a button (for example)
        button = QPushButton("Click Me")
        layout.addWidget(button)

        # Disable the minimize button
        self.setWindowFlag(Qt.WindowFlags.WindowMinimizeButtonHint, False)

if __name__ == "__main__":
	from PySide6.QtWidgets import QApplication
	app = QApplication([])
	window = MyMainWindow()
	window.show()
	app.exec_()