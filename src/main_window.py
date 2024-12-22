from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow,QWidget,QPushButton,QVBoxLayout,
							   QStatusBar,QLabel,QHBoxLayout,QLineEdit,QComboBox,
							   QSizePolicy)

from .scrollable_button_list import ScrollableButtonList

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		#self.setFixedHeight(0)
		#print(self.minimumSize())
		#print(self.sizePolicy())
		#self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Minimum)
		#self.setSizePolicy(Qt.)
		#self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint)

#		button.clicked.connect(self.button_clicked)
#		button.pressed.connect(self.button_pressed)
#		button.released.connect(self.button_released)

		################################

		lbl_issues = QLabel('Issues')
		cmb_issues = QComboBox()
		lay_issues = QHBoxLayout()
		lay_issues.addWidget(lbl_issues)
		lay_issues.addWidget(cmb_issues)

		lbl_time = QLabel('Time')
		txt_time = QLineEdit()
		lay_time = QHBoxLayout()
		lay_time.addWidget(lbl_time)
		lay_time.addWidget(txt_time)

		lbl_comment = QLabel('Comment')
		txt_comment = QLineEdit()
		lay_comment = QHBoxLayout()
		lay_comment.addWidget(lbl_comment)
		lay_comment.addWidget(txt_comment)

		lbl_dates = QLabel('Dates')
		txt_dates = QLineEdit()
		lay_dates = QHBoxLayout()
		lay_dates.addWidget(lbl_dates)
		lay_dates.addWidget(txt_dates)

		btn_upload = QPushButton("Upload Work Log")
		btn_save = QPushButton("Save Work Log")
		lay_buttons = QHBoxLayout()
		lay_buttons.addWidget(btn_upload)
		lay_buttons.addWidget(btn_save)

		################################

		layout = QVBoxLayout()
		layout.addLayout(lay_issues)
		layout.addLayout(lay_time)
		layout.addLayout(lay_comment)
		layout.addLayout(lay_dates)
		layout.addLayout(lay_buttons)

		################################

		lst_buttons = ScrollableButtonList()

		button = QPushButton("Button1")
		button.clicked.connect(self.button_clicked)
		lst_buttons.add_button(button)

		button = QPushButton("Button2")
		button.clicked.connect(self.button_clicked)
		lst_buttons.add_button(button)

		main_layout = QHBoxLayout()
		main_layout.addLayout(layout)
		main_layout.addWidget(lst_buttons)

		################################

		main_widget = QWidget()
		main_widget.setLayout(main_layout)

		statusbar = QStatusBar()
		self.setStatusBar(statusbar)
		ready = QLabel("Ready")
		statusbar.addWidget(ready)

		self.setWindowTitle("My Main Window")
#		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
#		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
		self.setCentralWidget(main_widget)

	def button_clicked(self):
		button = self.sender()
		print(button.text())
		print("Button Clicked")