from typing import Tuple
from PySide6.QtGui import QAction, QIcon, QKeyEvent, Qt
from PySide6.QtWidgets import QDialog, QLabel, QMainWindow, QWidget
from data.engine import ImageEditorScene
from data.template.design import Ui_ImageInfoDialog, Ui_MainWindow, Ui_ResizeDialog, Ui_SettingsDialog
import json


class ImageEditorMainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, parent: QMainWindow = None) -> None:
        """Initializes the class"""
        super().__init__(parent)
        
        self.window_title = "egamI Spell"

        self.read_only = False
        self.supported_formats = ["JPG", "JPEG", "PNG", "BMP", "PPM"]
        self.unsupported_formats = ["GIF", "PBM", "PGM"]
        self.supported_modes = ["RGB", "RGBA"]
        self.file_filter = "Image File (*.jpg *.jpeg *.png *.bmp *.ppm *.gif *.pbm *.pgm)"
        
        self.engine = ImageEditorScene()
        self._scale_factor = 1.0

        self.writable_only: list[QAction] = []
        self.image_required: list[QAction] = []
        
        self.settings_file = "data/settings.json"
        self.settings = {
            "config": {
                "autoFitInView": True,
                "filePathInTitle": False,
                "keepAspectRatioChoice": False,
                "lastLocationOpenned": True,
            },
            "behavior": {
                "location": '',
                "choice": True
            }
        }
        try:
            self.open_settings()
        except FileNotFoundError:
            self.save_settings()

        self.setupUi()
    
    def save_settings(self) -> None:
        """Save settings changes"""
        with open(self.settings_file, "w") as file:
            file.write(json.dumps(self.settings, indent=4))
    
    def open_settings(self) -> None:
        """Get settings from file"""
        with open(self.settings_file) as file:
            self.settings.update(json.loads(file.read()))

    def change_title(self, text: str) -> None:
        """Change window title"""
        self.setWindowTitle(f"{self.window_title} – {text}")
    
    def toolbar_action(self, icon: QIcon, text: str, status_tip: str, disabled: bool = True, required: bool = True, shortcut: str = None, writable_only: bool = True) -> QAction:
        """Add a action to toolbar"""
        action = QAction(self)
        action.setIcon(icon)
        action.setText(text)
        if disabled:
            action.setDisabled(True)
            if required:
                if writable_only:
                    self.writable_only.append(action)
                else:
                    self.image_required.append(action)
        if shortcut:
            action.setShortcut(shortcut)
            shortcut = shortcut.replace('++', ' +') if '++' in shortcut else shortcut.replace('+', ' ')
            status_tip += f"   [{shortcut}]"
        action.setStatusTip(status_tip)
        
        self.toolBar.addAction(action)
        return action
    
    def statusbar_label(self, text: str) -> QLabel:
        """Add a label to statusbar"""
        label = QLabel(text, self)

        self.statusBar().addPermanentWidget(label)
        return label
    
    def setupUi(self) -> None:
        """Setup basic GUI aspects"""
        super().setupUi(self)
        self.setWindowTitle(self.window_title)
        self.setWindowIcon(QIcon("data/icons/logo.png"))
        self.setWindowState(Qt.WindowMaximized)
        with open(f"data/styles/styles.css") as file:
            self.setStyleSheet(file.read())

        self.actionOpen = self.toolbar_action(QIcon("data/icons/open.png"), "Open", "Open image file", False, shortcut="Ctrl+O")
        self.actionSave = self.toolbar_action(QIcon("data/icons/save.png"), "Save", "Save the image as the same file", shortcut="Ctrl+S")
        self.actionSaveAs = self.toolbar_action(QIcon("data/icons/saveas.png"), "Save As...", "Save the image as a different file", shortcut="Ctrl+Shift+S")
        self.toolBar.addSeparator()
        self.actionResize = self.toolbar_action(QIcon("data/icons/resize.png"), "Resize Image", "Resize image or scale", shortcut="Ctrl+R")
        self.actionHorizontalReflect = self.toolbar_action(QIcon("data/icons/horizontal_reflect.png"), "Horizontal Reflect", "Flip the image horizontally")
        self.actionVerticalReflect = self.toolbar_action(QIcon("data/icons/vertical_reflect.png"), "Vertical Reflect", "Flip the image vertically")
        self.actionRotate90Right = self.toolbar_action(QIcon("data/icons/rotate90right.png"), "Rotate 90° Right", "Flip the image in 90° clockwise")
        self.actionRotate90Left = self.toolbar_action(QIcon("data/icons/rotate90left.png"), "Rotate 90° Left", "Flip the image in 90° anticlockwise")
        self.toolBar.addSeparator()
        self.actionGrayscale = self.toolbar_action(QIcon("data/icons/grayscale.png"), "Grayscale", "Set image to grayscale")
        self.actionSepia = self.toolbar_action(QIcon("data/icons/sepia.png"), "Sepia", "Set sepia color")
        self.actionBlur = self.toolbar_action(QIcon("data/icons/blur.png"), "Blur", "Blur the image")
        self.actionEdges = self.toolbar_action(QIcon("data/icons/edges.png"), "Edges", "Find image edges")
        self.toolBar.addSeparator()
        self.actionFitOnScreen = self.toolbar_action(QIcon("data/icons/fit_normal.png"), "Toggle fit / normal", "Toggle fit on view / normal size", shortcut="Ctrl+T", writable_only=False)
        self.actionZoomIn = self.toolbar_action(QIcon("data/icons/zoom_in.png"), "Zoom In", "Increases scale in 25%", shortcut="Ctrl++", writable_only=False)
        self.actionZoomOut = self.toolbar_action(QIcon("data/icons/zoom_out.png"), "Zoom Out", "Decreases scale in 25%", shortcut="Ctrl+-", writable_only=False)
        self.toolBar.addSeparator()
        self.actionRedo = self.toolbar_action(QIcon("data/icons/redo.png"), "Redo", "Undo action", shortcut="Ctrl+Shift+Z", required=False)
        self.actionUndo = self.toolbar_action(QIcon("data/icons/undo.png"), "Undo", "Redo action", shortcut="Ctrl+Z", required=False)
        self.toolBar.addSeparator()
        self.actionImageInfo = self.toolbar_action(QIcon("data/icons/image_info.png"), "Image info", "Image info", shortcut="Ctrl+I", writable_only=False)
        self.actionSettings = self.toolbar_action(QIcon("data/icons/settings.png"), "Settings", "Settings", False, shortcut="Ctrl+'")
        self.actionAbout = self.toolbar_action(QIcon("data/icons/about.png"), "About", "About the program", False, shortcut="Ctrl+A")
        self.actionExit = self.toolbar_action(QIcon("data/icons/exit.png"), "Exit", "Exit", False, shortcut="Ctrl+Q")

        self.fileSizeLabel = self.statusbar_label("Size")
        self.fileSizeLabel.hide()

    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen function"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Custom key functions"""
        if event.key() == Qt.Key_F or event.key() == Qt.Key_F11:
            self.toggle_fullscreen()


class ImageEditorResize(Ui_ResizeDialog, QDialog):
    def __init__(self, width: int, height: int, parent: QWidget = None) -> None:
        """Initizalizes the class"""
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(QIcon("data/icons/resize.png"))

        self.width_ratio = width / height
        self.height_ratio = height / width

        self.widthBox.setValue(width)
        self.heightBox.setValue(height)

        self.widthBox.valueChanged.connect(self.keep_aspect_ratio_when_width_changes)
        self.heightBox.valueChanged.connect(self.keep_aspect_ratio_when_height_changes)

        self.submitButton.accepted.connect(self.accept)
        self.widthBox.setFocus()
    
    def keep_aspect_ratio_when_width_changes(self) -> None:
        """Called when width is modified, keeping the height aspect ratio"""
        if not self.keepAspectRatio.isChecked():
            return

        self.heightBox.blockSignals(True)
        self.heightBox.setValue(int(self.height_ratio * self.widthBox.value()))
        self.heightBox.blockSignals(False)
    
    def keep_aspect_ratio_when_height_changes(self) -> None:
        """Called when height is modified, keeping the width aspect ratio"""
        if not self.keepAspectRatio.isChecked():
            return
        
        self.widthBox.blockSignals(True)
        self.widthBox.setValue(int(self.width_ratio * self.heightBox.value()))
        self.widthBox.blockSignals(False)
    
    @property
    def info(self) -> Tuple[int, int]:
        """Must be called to get the values from the user input"""
        return self.widthBox.value(), self.heightBox.value()


class ImageEditorImageInfo(Ui_ImageInfoDialog, QDialog):
    def __init__(self, info: dict, parent: QWidget) -> None:
        """Initializes the class and show image info"""
        super().__init__(parent)
        super().setupUi(self)

        self.setWindowIcon(QIcon("data/icons/image_info.png"))

        self.locationLine.setText(info["location"])
        self.nameLine.setText(info["name"])
        self.modeLine.setText(info["mode"])
        self.formatLine.setText(info["format"])
        self.descriptionLine.setText(info["description"])
        self.extensionLine.setText(info["extension"])


class ImageEditorSettings(Ui_SettingsDialog, QDialog):
    def __init__(self, settings: dict, parent: QWidget) -> None:
        """Initializes the class"""
        super().__init__(parent)
        super().setupUi(self)

        self.setWindowIcon(QIcon("data/icons/settings.png"))

        self.settings = settings
        self.keepAspectRatioChoice.setChecked(settings["config"]["keepAspectRatioChoice"])
        self.lastLocationOpenned.setChecked(settings["config"]["lastLocationOpenned"])
        self.filePathInTitle.setChecked(settings["config"]["filePathInTitle"])
        self.autoFitInView.setChecked(settings["config"]["autoFitInView"])
    
    @property
    def info(self) -> dict:
        self.settings["config"]["keepAspectRatioChoice"] = self.keepAspectRatioChoice.isChecked()
        self.settings["config"]["lastLocationOpenned"] = self.lastLocationOpenned.isChecked()
        self.settings["config"]["filePathInTitle"] = self.filePathInTitle.isChecked()
        self.settings["config"]["autoFitInView"] = self.autoFitInView.isChecked()
        return self.settings
