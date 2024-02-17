from PySide6.QtCore import Qt, QSize

from PySide6.QtGui import (
    QAction, 
    QIcon,
    QPixmap, 
    QResizeEvent
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QToolBar,
    QFileDialog,
    QFileSystemModel,
    QListView,
    QHBoxLayout,
    QStyledItemDelegate, 
    QFileIconProvider
)

from pokatlas import decomp

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400

class Label(QLabel):

    def __init__(self):
        super(Label, self).__init__()
        self.pixmap_width: int = 1
        self.pixmapHeight: int = 1

    def setPixmap(self, pm: QPixmap) -> None:
        self.pixmap_width = pm.width()
        self.pixmapHeight = pm.height()

        self.updateMargins()
        super(Label, self).setPixmap(pm)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.updateMargins()
        super(Label, self).resizeEvent(a0)

    def updateMargins(self):
        if self.pixmap() is None:
            return
        pixmapWidth = self.pixmap().width()
        pixmapHeight = self.pixmap().height()
        if pixmapWidth <= 0 or pixmapHeight <= 0:
            return
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        if w * pixmapHeight > h * pixmapWidth:
            m = int((w - (pixmapWidth * h / pixmapHeight)) / 2)
            self.setContentsMargins(m, 0, m, 0)
        else:
            m = int((h - (pixmapHeight * w / pixmapWidth)) / 2)
            self.setContentsMargins(0, m, 0, m)

class NameDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if isinstance(index.model(), QFileSystemModel):
            if not index.model().isDir(index):
                option.text = index.model().fileInfo(index).baseName()

    def setEditorData(self, editor, index):
        if isinstance(index.model(), QFileSystemModel):
            if not index.model().isDir(index):
                editor.setText(index.model().fileInfo(index).baseName())
            else:
                super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(model, QFileSystemModel):
            fi = model.fileInfo(index)
            if not model.isDir(index):
                model.setData(index, editor.text() + "." + fi.suffix())
            else:
                super().setModelData(editor, model.index)

class EmptyIconProvider(QFileIconProvider):
    def icon(self, _):
        return QIcon()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.atlas_dir = None
        self.selected_sprite_filename = None

        self.setWindowIcon(QIcon('./ui/icon.png'))
        self.setWindowTitle('Pokatlas')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.toolbar = QToolBar('Main Toolbar')
        # self.toolbar.setIconSize(QSize(16,16))
        self.toolbar.setMovable(False)
        self.toolbar.toggleViewAction().setEnabled(False)
        self.addToolBar(self.toolbar)

        self.open_atlas_action = QAction('Open Atlas', self)
        self.open_atlas_action.triggered.connect(self.open_atlas_slot)
        self.toolbar.addAction(self.open_atlas_action)

        self.replace_action = QAction('Replace Sprite', self)
        self.replace_action.triggered.connect(self.replace_sprite)
        self.replace_action.setVisible(False)
        self.toolbar.addAction(self.replace_action)

        self.test_atlas()

    def display_atlas(self):
        widget = QWidget(self)
        model = QFileSystemModel()
        model.setIconProvider(EmptyIconProvider())
        model.setRootPath(f'{self.atlas_dir}/sprites')

        self.sprite_list = QListView()
        self.sprite_list.setModel(model)
        self.sprite_list.setRootIndex(model.index(f'{self.atlas_dir}/sprites'))
        delegate = NameDelegate(self.sprite_list)
        self.sprite_list.setItemDelegate(delegate)
        self.sprite_list.setViewMode(QListView.ViewMode.ListMode)
        self.sprite_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.sprite_list.setMinimumWidth(WINDOW_WIDTH // 3.5)
        self.sprite_list.clicked.connect(self.list_clicked)

        layout = QHBoxLayout(widget)
        layout.addWidget(self.sprite_list, alignment=Qt.AlignmentFlag.AlignLeft)

        self.sprite_image_label = Label() 
        pixmap = QPixmap(f'{self.atlas_dir}/main.png')
        self.sprite_image_label.setPixmap(pixmap.scaled(QSize(WINDOW_WIDTH, WINDOW_HEIGHT), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.sprite_image_label.setScaledContents(True)

        layout.addWidget(self.sprite_image_label, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(widget)

    def open_atlas_slot(self):
        self.atlas_file = QFileDialog.getOpenFileName(self, 'Open main.atlas')[0]
        self.atlas_dir = '/'.join(self.atlas_file.strip().split('/')[:-1])
        decomp(self.atlas_file)
        self.display_atlas()

    def test_atlas(self):
        self.atlas_file = '/home/seth/coding/pokatlas/atlas/default/main.atlas'
        self.atlas_dir = '/'.join(self.atlas_file.strip().split('/')[:-1])
        decomp(self.atlas_file)
        self.display_atlas()

    def list_clicked(self, idx):
        if not self.replace_action.isVisible():
            self.replace_action.setVisible(True)

        self.selected_sprite_filename = idx.data()

        pixmap = QPixmap(f'{self.atlas_dir}/sprites/{self.selected_sprite_filename}')
        if pixmap.size().width() <= 50:
            ratio = 7
        elif pixmap.size().width() <= 60:
            ratio = 6
        else:
            ratio = 5

        self.sprite_image_label.setPixmap(pixmap.scaled(QSize(pixmap.size().width() * ratio, pixmap.size().height() * ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
        self.sprite_image_label.setScaledContents(False)


    def replace_sprite(self, idx):
        print(self.selected_sprite_filename)