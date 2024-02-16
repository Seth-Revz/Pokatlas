from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar
)

from pokatlas import decomp

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('./ui/icon.png'))
        self.setWindowTitle('Pokatlas')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        toolbar = QToolBar('Main Toolbar')
        # toolbar.setIconSize(QSize(16,16))
        toolbar.setMovable(False)
        toolbar.toggleViewAction().setEnabled(False)
        self.addToolBar(toolbar)

        open_atlas_action = QAction('Open Atlas', self)
        open_atlas_action.setStatusTip("This is your button")
        open_atlas_action.triggered.connect(self.open_atlas_slot)
        toolbar.addAction(open_atlas_action)

    def open_atlas_slot(self):
        decomp('default')