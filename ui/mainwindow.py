from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar
)


WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('./ui/icon.png'))
        self.setWindowTitle('Pokatlas')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        toolbar = QToolBar('Main Toolbar')
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)

        button_action = QAction('Open Atlas', self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        toolbar.addAction(button_action)

    def onMyToolBarButtonClick(self, s):
        print("click", s)