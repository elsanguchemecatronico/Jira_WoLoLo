import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QPushButton, QWidget

class ScrollableButtonList(QWidget):
	def __init__(self):
		super().__init__()

		self.__button_list = QVBoxLayout()
		#self.__button_list.addStretch()
		self.__button_list.setAlignment(Qt.AlignTop)

		container = QWidget()
		container.setLayout(self.__button_list)

		scroll_area = QScrollArea()
		scroll_area.setWidget(container)
		scroll_area.setWidgetResizable(True)

		layout = QVBoxLayout()
		layout.addWidget(scroll_area)

		self.setLayout(layout)

	def add_button(self,btn):
		self.__button_list.addWidget(btn)
		#self.__button_list.insertWidget(-2,btn)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = ScrollableButtonList()
	window.add_button("hola")
	window.show()
	sys.exit(app.exec())



	scroll_area.setAlignment(Qt.AlignHCenter | Qt.AlignTop)