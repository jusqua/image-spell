from typing import Union
from PIL import Image, ImageFilter
from PySide6.QtCore import QDir, QEvent, QObject, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QFileDialog, QGraphicsView, QMainWindow, QMessageBox
from data.dialog import ImageEditorImageInfo, ImageEditorMainWindow, ImageEditorResize, ImageEditorSettings
from data.engine import ImageEditorControlTag, ImageEditorFilterTag, ImageEditorSceneTag, ImageEditorTransformTag
import numpy as np
import sys


class ImageEditor(ImageEditorMainWindow):
    def __init__(self, parent: QMainWindow = None) -> None:
        """Initializes the class"""
        super().__init__(parent)
        self.setup_action()
        self.graphicsView.installEventFilter(self)
    
    @property
    def scale_factor(self) -> float:
        """Scale factor getter"""
        return self._scale_factor
    
    @scale_factor.setter
    def scale_factor(self, value: Union[int, float]) -> None:
        """Scale factor setter"""
        self._scale_factor = value
        if self._scale_factor <= 0.05:
            self._scale_factor = 0.05
            self.actionZoomOut.setDisabled(True)
        elif self._scale_factor >= 8.0:
            self._scale_factor = 8.0
            self.actionZoomIn.setDisabled(True)
        else:
            self.actionZoomIn.setDisabled(False)
            self.actionZoomOut.setDisabled(False)

    @property
    def location(self) -> str:
        """Get settings path"""
        if self.settings["config"]["lastLocationOpenned"] and self.settings["behavior"]["location"]:
            return self.settings["behavior"]["location"]
        else:
            return QDir.homePath()
    
    @location.setter
    def location(self, value: str) -> None:
        """Set settings path"""
        if self.settings["config"]["lastLocationOpenned"]:
            self.settings["behavior"]["location"] = value
        else:
            self.settings["behavior"]["location"] = ''
    
    def scale(self) -> None:
        """Scale image from scale factor (decorator)"""
        self.graphicsView.resetTransform()
        self.graphicsView.scale(self.scale_factor, self.scale_factor)
        self.fileSizeLabel.setText(f"{self.engine.info['size']} ({int(self.scale_factor * 100)}%)")

    def scalewrap(func):
        """Scale (decorator)"""
        def wrap(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.scale()
        return wrap

    def update(func):
        """Update image data (decorator)"""
        def wrap(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            if response:
                return
            
            self.graphicsView.setScene(self.engine.scene)

            if self.settings["config"]["filePathInTitle"]:
                combine_to_title = self.engine.info["path"]
            else:
                combine_to_title = self.engine.info["name_with_extension"]
            if self.engine.changed:
                combine_to_title += '*'
            if not self.writable:
                combine_to_title += ' (Read-only)'
            self.change_title(combine_to_title)
            
            self.control_action(ImageEditorControlTag.STATE)
            if self.settings["config"]["autoFitInView"] and \
                self.engine.scene.itemsBoundingRect().size().toTuple() > self.graphicsView.size().toTuple():
                self.scale_factor = self.fit_scale()
            else:
                self.scale_factor = 1.0
            self.scale()
        return wrap

    @update
    def save_changes(self, tag: ImageEditorControlTag) -> None:
        """Save changes"""
        if tag == ImageEditorControlTag.SAVE:
            if self.engine.changed and self.engine.first_save:
                tag = ImageEditorControlTag.SAVEAS
            elif not self.engine.changed:
                return
        
        image = None
        if tag == ImageEditorControlTag.SAVEAS:
            image, _ = QFileDialog.getSaveFileName(
                self.centralwidget,
                "Save file as",
                self.engine.info["path"],
                self.file_filter
            )

            if not image:
                return
            elif self.engine.info["extension"] not in image:
                image += self.engine.info["extension"]
        
        self.engine.save(image)
        self.location = self.engine.info["location"]

    @update
    def set_settings(self) -> bool:
        """Set custom settings for the program"""
        dialog = ImageEditorSettings(self.settings, self.centralwidget)
        if dialog.exec():
            self.settings.update(dialog.info)
        
        if self.engine.empty:
            return True

    @update
    def open_file(self) -> bool:
        """Open image"""
        if not self.engine.empty and self.engine.changed:
            dialog = QMessageBox.warning(
                self.centralwidget,
                "Open without save",
                "<p>Are you sure do you want to open another file without save any changes?</p>", 
                QMessageBox.Yes | QMessageBox.No
            )
            if dialog == QMessageBox.No:
                return True

        image, _ = QFileDialog.getOpenFileName(
            self.centralwidget,
            "Open image",
            self.location,
            self.file_filter
        )

        if not image:
            return True

        self.engine.new(image)
        self.control_action(ImageEditorControlTag.OPEN)
        self.location = self.engine.info["location"]

    @update
    def resize_image(self) -> bool:
        """Resize image from dialog input"""
        width, height = self.engine.pixmap.width(), self.engine.pixmap.height()
        dialog = ImageEditorResize(width, height, self.centralwidget)
        if self.settings["config"]["keepAspectRatioChoice"]:
            dialog.keepAspectRatio.setChecked(self.settings["behavior"]["choice"])
        
        accept = dialog.exec()
        if accept:
            new_width, new_height = dialog.info
            self.settings["behavior"]["choice"] = dialog.keepAspectRatio.isChecked()
            if width == new_width and new_height == height:
                return True
        
        try:
            pixmap = self.engine.pixmap.scaled(new_width, new_height)
        except UnboundLocalError:
            return

        self.engine.add(pixmap)

    @update
    def filter_image(self, tag: ImageEditorFilterTag) -> None:
        """Filter image (QPixmap) based on filter tag"""
        image = Image.fromqpixmap(self.engine.pixmap)
        mode = image.mode
        if mode == "RGBA":
            alpha = image.getchannel('A')

        if tag is ImageEditorFilterTag.BLUR:
            result = image.filter(ImageFilter.BLUR)
        elif tag is ImageEditorFilterTag.EDGES:
            result = image.filter(ImageFilter.FIND_EDGES)
        elif tag is ImageEditorFilterTag.GRAYSCALE:
            result = image.convert('L')
        elif tag is ImageEditorFilterTag.SEPIA:
            pix = np.array(image)
            if mode == "RGBA":
                sepia_filter = np.array([[.393, .769, .189, 0], [.349, .686, .168, 0], [.272, .534, .131, 0]])
            else:    
                sepia_filter = np.array([[.393, .769, .189], [.349, .686, .168], [.272, .534, .131]])
            pix: np.ndarray = pix.dot(sepia_filter.T)
            pix[pix>255] = 255
            result = Image.fromarray(pix.astype(np.uint8))

        if mode == "RGBA":
            result.putalpha(alpha)
        
        self.engine.add(result.toqpixmap())
    
    @update
    def transform_image(self, tag: ImageEditorTransformTag) -> None:
        """Tranform image (QPixmap) based on transform tag"""
        image = np.array(Image.fromqpixmap(self.engine.pixmap))
        if tag is ImageEditorTransformTag.HORIZONTALFLIP:
            image = np.fliplr(image)
        elif tag is ImageEditorTransformTag.VERTICALFLIP:
            image = np.flipud(image)
        elif tag is ImageEditorTransformTag.CLOCKROTATE:
            image = np.rot90(image, 1)
        elif tag is ImageEditorTransformTag.ANTICLOCKROTATE:
            image = np.rot90(image, -1)
        self.engine.add(Image.fromarray(image).toqpixmap())

    @update
    def undo(self) -> None:
        """Undo changes"""
        self.engine.undo()

    @update
    def redo(self) -> None:
        """Redo changes"""
        self.engine.redo()

    def fit_scale(self) -> float:
        s_width, s_height = self.engine.scene.itemsBoundingRect().size().toTuple()
        gv_width, gv_height = self.graphicsView.rect().size().toTuple()
        return min(gv_width / s_width, gv_height / s_height)

    @scalewrap
    def toggle_fit_normal_screen(self) -> None:
        """Toggle fit or normal in view"""
        transform = self.graphicsView.transform()
        transform.reset()
        if transform == self.graphicsView.transform():
            self.scale_factor = self.fit_scale()
        else:
            self.scale_factor = 1.0
    
    @scalewrap
    def zoom_in(self, factor: int = 0.25) -> None:
        """Zoom In graphics view"""
        self.scale_factor += factor

    @scalewrap
    def zoom_out(self, factor: int = 0.25) -> None:
        """Zoom Out graphics view"""
        self.scale_factor -= factor
    
    def image_info(self) -> None:
        """Show image information in dialog"""
        ImageEditorImageInfo(self.engine.info, self.centralwidget).exec()

    def setup_action(self) -> None:
        """Setup action functionalities"""
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSave.triggered.connect(lambda: self.save_changes(ImageEditorControlTag.SAVE))
        self.actionSaveAs.triggered.connect(lambda: self.save_changes(ImageEditorControlTag.SAVEAS))
        
        self.actionResize.triggered.connect(self.resize_image)
        self.actionHorizontalReflect.triggered.connect(lambda: self.transform_image(ImageEditorTransformTag.HORIZONTALFLIP))
        self.actionVerticalReflect.triggered.connect(lambda: self.transform_image(ImageEditorTransformTag.VERTICALFLIP))
        self.actionRotate90Right.triggered.connect(lambda: self.transform_image(ImageEditorTransformTag.CLOCKROTATE))
        self.actionRotate90Left.triggered.connect(lambda: self.transform_image(ImageEditorTransformTag.ANTICLOCKROTATE))
        
        self.actionGrayscale.triggered.connect(lambda: self.filter_image(ImageEditorFilterTag.GRAYSCALE))
        self.actionSepia.triggered.connect(lambda: self.filter_image(ImageEditorFilterTag.SEPIA))
        self.actionBlur.triggered.connect(lambda: self.filter_image(ImageEditorFilterTag.BLUR))
        self.actionEdges.triggered.connect(lambda: self.filter_image(ImageEditorFilterTag.EDGES))

        self.actionFitOnScreen.triggered.connect(self.toggle_fit_normal_screen)
        self.actionZoomIn.triggered.connect(self.zoom_in)
        self.actionZoomOut.triggered.connect(self.zoom_out)

        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)

        self.actionImageInfo.triggered.connect(self.image_info)
        self.actionSettings.triggered.connect(self.set_settings)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.about)

    @property
    def writable(self) -> bool:
        return True \
               if self.engine.info["format"] in self.supported_formats and \
                  self.engine.info["mode"] in self.supported_modes \
               else False
    
    def control_action(self, tag: ImageEditorControlTag) -> None:
        """Enable action by tag"""
        if tag == ImageEditorControlTag.OPEN:
            writable = self.writable
            for widget in self.writable_only:
                widget.setEnabled(writable)
            for widget in self.image_required:
                widget.setEnabled(True)
            self.fileSizeLabel.show()
        
        elif tag == ImageEditorControlTag.STATE:
            if self.engine.state == ImageEditorSceneTag.FIRST:
                self.actionUndo.setDisabled(True)
                self.actionRedo.setEnabled(True)
            elif self.engine.state == ImageEditorSceneTag.LAST:
                self.actionUndo.setDisabled(False)
                self.actionRedo.setEnabled(False)
            elif self.engine.state == ImageEditorSceneTag.MIDDLE:
                self.actionUndo.setDisabled(False)
                self.actionRedo.setEnabled(True)
            else:
                self.actionUndo.setDisabled(True)
                self.actionRedo.setEnabled(False)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Custom events"""
        modifier = QApplication.keyboardModifiers()
        if modifier != Qt.NoModifier:
            if modifier == Qt.ControlModifier:
                if event.type() == QEvent.Wheel:
                    delta = event.angleDelta().y()
                    if delta > 0:
                        self.zoom_in(0.05)
                    elif delta < 0:
                        self.zoom_out(0.05)
                    return True
            if modifier == Qt.ShiftModifier:
                self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
            return False
        else:
            self.graphicsView.verticalScrollBar().blockSignals(False)
            self.graphicsView.horizontalScrollBar().blockSignals(False)
            self.graphicsView.setDragMode(QGraphicsView.NoDrag)
            return False

    def closeEvent(self, event: QCloseEvent) -> None:
        """Custom close event | Confirm exit without save changes"""
        if not self.engine.changed:
            self.save_settings()
            return
        
        dialog = QMessageBox.warning(
            self.centralwidget, 
            "Exit without save", 
            "<p>Are you sure do you want to exit without save any changes?</p>", 
            QMessageBox.Yes | QMessageBox.No
        )

        if dialog == QMessageBox.Yes:
            self.save_settings()
            event.accept()
        else:
            event.ignore()

    def about(self) -> None:
        """About the program"""
        repo = 'href="https://github.com/jusqua"'
        license = 'href="https://opensource.org/licenses/MIT"'
        a = 'style="text-decoration: none; color: crimson;"'
        p = 'style="margin: 0px; text-align: justify;"'
        h = 'style="text-align: center;"'
        QMessageBox.about(
            self.centralwidget,
            "About",
            f"<h3 {h}>Hello world from <a {a} {repo}>jusqua</a>!</h3>"
            f"<p {p}>This program is a experience for learn Python3 and Qt,</p>"
            f"<p {p}>and I want to implement such features to this project yet,</p>"
            f"<p {p}>feel free to use and abuse this code as well.</p>"
            f"<h4 {h}>Keys there are not exposed</h4>"
            f"<p {p}>Press <b>Ctrl + Mouse Wheel</b> to Zoom In/Out</p>"
            f"<p {p}>Press <b>Shift + Mouse</b> to Hand Drag Navigate</p>"
            f"<p {p}>Press <b>F11</b> to Toogle Fullscreen</p>"
            f"<h5 {h}>Licenced under <a {a} {license}>MIT Licence</a></h5>"
            f"<h5 {h}>Copyright &copy; Ádrian Gama 2021</h5>"
        )


def main() -> None:
    """Main function"""
    app = QApplication(sys.argv)
    mw = ImageEditor()
    mw.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
