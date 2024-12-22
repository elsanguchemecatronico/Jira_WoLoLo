from PySide6.QtCore import QMetaObject, Qt, QTimer, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.i = 0

        self.button = QPushButton("push me!")
        self.button.clicked.connect(self.clicked)

        self.label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.label)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint)
        self.clicked()
        self.show()

    # @Slot()
    # def adjustSize(self):
    #     super().adjustSize()

    def clicked(self):
        npix = 500 - 50 * self.i
        self.label.setPixmap(QPixmap(npix, npix))
        self.i += 1

        # # As in https://stackoverflow.com/a/23954088/880783 - does not work
        # QMetaObject.invokeMethod(self, "adjustSize")

        # This works!
        QTimer.singleShot(0, self.adjustSize)


app = QApplication()
win = Window()
app.exec()