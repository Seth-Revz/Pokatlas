from PySide6.QtCore import (
    Qt,
    QDir,
    QFile,
    QPoint,
    QProcess,
    QSize,
)

from PySide6.QtGui import (
    QAction,
    QDesktopServices,
    QIcon,
    QPixmap, 
    QResizeEvent,
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
    QVBoxLayout,
    QStyledItemDelegate, 
    QFileIconProvider,
    QSizePolicy,
    QMessageBox,
)

from pokatlas import decomp, rebuild
import platform

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
        self.toolbar.setMovable(False)
        self.toolbar.toggleViewAction().setEnabled(False)
        self.addToolBar(self.toolbar)

        self.open_atlas_action = QAction('Open Atlas', self)
        self.open_atlas_action.triggered.connect(self.open_atlas)
        self.toolbar.addAction(self.open_atlas_action)

        self.replace_action = QAction('Replace Sprite', self)
        self.replace_action.triggered.connect(self.single_replace_sprite)
        self.replace_action.setVisible(False)
        self.toolbar.addAction(self.replace_action)

        self.save_atlas_action = QAction('Save Atlas', self)
        self.save_atlas_action.triggered.connect(self.save_atlas)
        self.save_atlas_action.setVisible(False)
        self.toolbar.addAction(self.save_atlas_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        self.open_sprite_folder_action = QAction('Sprite Folder', self)
        self.open_sprite_folder_action.triggered.connect(self.open_sprite_folder)
        self.open_sprite_folder_action.setVisible(False)
        self.toolbar.addAction(self.open_sprite_folder_action)

        self.mass_replace_action = QAction('Mass Replace', self)
        self.mass_replace_action.triggered.connect(self.mass_replace_sprites)
        self.mass_replace_action.setVisible(False)
        self.toolbar.addAction(self.mass_replace_action)

        widget = QWidget(self)
        layout = QVBoxLayout(widget)

        label = QLabel()
        label.setText("<font color='grey'>Open main.atlas<br /><br />Replace Sprites<br /><br />Save Spritesheet</font>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = self.font()
        font.setPointSize(13)
        label.setFont(font)

        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(widget)


    def display_atlas(self):
        widget = QWidget(self)
        self.model = QFileSystemModel()
        self.model.setIconProvider(EmptyIconProvider())
        self.model.setRootPath(f'{self.atlas_dir}/sprites')

        self.sprite_list = QListView()
        self.sprite_list.setModel(self.model)
        self.sprite_list.setRootIndex(self.model.index(f'{self.atlas_dir}/sprites'))
        delegate = NameDelegate(self.sprite_list)
        self.sprite_list.setItemDelegate(delegate)
        self.sprite_list.setViewMode(QListView.ViewMode.ListMode)
        self.sprite_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.sprite_list.setMinimumWidth(WINDOW_WIDTH // 3.5)
        self.sprite_list.selectionModel().currentChanged.connect(self.list_clicked)

        layout = QHBoxLayout(widget)
        layout.addWidget(self.sprite_list, alignment=Qt.AlignmentFlag.AlignLeft)

        self.sprite_image_label = Label() 
        pixmap = QPixmap(f'{self.atlas_dir}/main.png')
        self.sprite_image_label.setPixmap(pixmap.scaled(QSize(WINDOW_WIDTH, WINDOW_HEIGHT), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.sprite_image_label.setScaledContents(True)

        layout.addWidget(self.sprite_image_label, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(widget)

        if self.replace_action.isVisible():
            self.replace_action.setVisible(False)
        if self.save_atlas_action.isVisible():
            self.save_atlas_action.setVisible(False)
        if not self.open_sprite_folder_action.isVisible():
            self.open_sprite_folder_action.setVisible(True)
        if not self.mass_replace_action.isVisible():
            self.mass_replace_action.setVisible(True)

    def open_atlas(self):

        atlas_filename = QFileDialog.getOpenFileName(self, 'Open main.atlas')[0]

        if atlas_filename == '':
            return

        self.atlas_file = atlas_filename
        self.atlas_dir = '/'.join(self.atlas_file.strip().split('/')[:-1])
        decomp(self.atlas_file)
        self.display_atlas()
        
        self.sprite_list.setCurrentIndex(self.sprite_list.indexAt(QPoint(0,0)))

    def save_atlas(self):
        rebuild(self.atlas_file)
        self.open_directory(f'{self.atlas_dir}/output')

    def list_clicked(self, current_selection, previous_selection):
        
        if not self.replace_action.isVisible():
            self.replace_action.setVisible(True)

        self.selected_sprite_filename = current_selection.data()
        
        self.refresh_sprite_preview()

    def refresh_sprite_preview(self):
        pixmap = QPixmap(f'{self.atlas_dir}/sprites/{self.selected_sprite_filename}')
        if pixmap.size().width() <= 50:
            ratio = 7
        elif pixmap.size().width() <= 60:
            ratio = 6
        else:
            ratio = 5

        self.sprite_image_label.setPixmap(pixmap.scaled(QSize(pixmap.size().width() * ratio, pixmap.size().height() * ratio), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
        self.sprite_image_label.setScaledContents(False)

    def single_replace_sprite(self, idx):
        size = QPixmap(f'{self.atlas_dir}/sprites/{self.selected_sprite_filename}').size()
        replacement_filename = QFileDialog.getOpenFileName(self, f'Select Replacement {self.selected_sprite_filename} - Size {size.width()}x{size.height()}')[0]
        
        if replacement_filename == '':
            return
        
        self.current_replacement_file = replacement_filename

        self.replace_sprite(self.current_replacement_file, f'{self.atlas_dir}/sprites/{self.selected_sprite_filename}')
        self.refresh_sprite_preview()

    def open_sprite_folder(self):
        self.open_directory(f'{self.atlas_dir}/sprites')

    def mass_replace_sprites(self):
        msgbox = QMessageBox()
        msgbox.setWindowIcon(QIcon('./ui/icon.png'))
        msgbox.setWindowTitle('Warning')
        msgbox.setText('Matching Sprite File Names' + ' '*30)
        msgbox.setInformativeText('Only files in the selected folder with names matching the dumped sprites will be replaced.')
        msgbox.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msgbox.setDefaultButton(QMessageBox.StandardButton.Ok)
        msgbox_return = msgbox.exec()

        if msgbox_return == QMessageBox.StandardButton.Cancel:
            return
        
        mass_replacement_folder = QFileDialog.getExistingDirectory(self, 'Select replacement sprites directory', self.atlas_dir)

        sprite_qdir = QDir(self.atlas_dir + '/sprites')
        sprite_files = sprite_qdir.entryList(filters=QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries)
        replacement_qdir = QDir(mass_replacement_folder)
        replacement_files = replacement_qdir.entryList(filters=QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries)

        for f in replacement_files:
            if f in sprite_files:
                self.replace_sprite(f'{mass_replacement_folder}/{f}', f'{self.atlas_dir}/sprites/{f}')
                self.sprite_list.setCurrentIndex(self.model.index(f'{self.atlas_dir}/sprites/{f}'))

        self.refresh_sprite_preview()

    def replace_sprite(self, src: str, dst: str):
        if not QFile.exists(dst) or QFile.remove(dst):
            if not QFile.copy(src, dst):
                print('Could not copy file')
                return False
            else:
                if not self.save_atlas_action.isVisible():
                    self.save_atlas_action.setVisible(True)
        else:
            print('Could not remove file')
            return False

    def open_directory(self, path: str):
        platform_os = platform.system()
        if platform_os == 'Windows':
            windows_is_shit = path.replace('/', '\\')
            QProcess.startDetached(f'explorer', arguments=[f"\e,{windows_is_shit}"])
        elif platform_os == 'Linux':
            QDesktopServices.openUrl(path)
        elif platform_os == 'Darwin':
            #No mac to test this so.
            QDesktopServices.openUrl(path)
        else:
            print('tf you running this on')
