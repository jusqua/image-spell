import os
from PIL import Image
from enum import Enum, auto
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QPixmap


class ImageEditorFilterTag(Enum):
    BLUR = auto()
    SEPIA = auto()
    GRAYSCALE = auto()
    EDGES = auto()


class ImageEditorTransformTag(Enum):
    HORIZONTALFLIP = auto()
    VERTICALFLIP = auto()
    CLOCKROTATE = auto()
    ANTICLOCKROTATE = auto()


class ImageEditorControlTag(Enum):
    OPEN = auto()
    SAVE = auto()
    SAVEAS = auto()
    STATE = auto()


class ImageEditorSceneTag(Enum):
    START = auto()
    FIRST = auto()
    LAST = auto()
    MIDDLE = auto()


class ImageEditorScene:
    def __init__(self) -> None:
        """Initializes the class"""
        self.changes: list[QPixmap] = []
        self.head: int = None
        self.tail: int = None
        self.scene = None
        self.path = ''
        self.info = {}
    
    def new(self, path: str) -> None:
        """Set new file"""
        image = QPixmap(path)

        self.head = 0
        self.tail = 0
    
        self.changes.clear()
        self.changes.append(image)

        self.set_scene()
        self.set_info(image, path)
    

    def set_scene(self) -> None:
        """Set scene from head tag"""
        self.scene = QGraphicsScene()
        self.scene.addPixmap(self.pixmap)
    
    def set_info(self, pixmap: QPixmap = None, path: str = None) -> None:
        """Set info about actual image state"""
        if pixmap:
            image = Image.fromqpixmap(pixmap)
            self.info["size"] = "%ix%i"%image.size
        
        if path:
            self.info["path"] = path
            self.info["location"], self.info["name_with_extension"] = os.path.split(path)
            self.info["name"], self.info["extension"] = os.path.splitext(self.info["name_with_extension"])
            self.info["extension_tag"] = self.info["extension"].split('.')[-1].upper()

            image = Image.open(path)
            self.info["description"] = image.format_description
            self.info["format"] = image.format
            self.info["mode"] = image.mode
    
    def add(self, pixmap: QPixmap) -> None:
        """Append new QPixmap"""
        if self.head != len(self.changes) - 1:
            self.changes = self.changes[:self.head + 1]
        
        self.head += 1
        self.changes.append(pixmap)

        self.set_scene()
        self.set_info(self.pixmap)

    def undo(self) -> None:
        """Backward one index"""
        if self.empty or self.head == 0:
            return

        self.head -= 1
        self.set_scene()
        self.set_info(self.pixmap)
    
    def redo(self) -> None:
        """Forward one index"""
        if self.empty or self.head >= len(self.changes):
            return
        
        self.head += 1
        self.set_scene()
        self.set_info(self.pixmap)
    
    def save(self, path: str = None) -> None:
        """Set save changes"""
        if path:
            self.pixmap.save(path)
            self.set_info(path=path)
        else:
            self.pixmap.save(self.info["path"], self.info["format"])
        
        self.tail = self.head

    @property
    def first_save(self):
        return not self.tail

    @property
    def empty(self) -> bool:
        return not self.changes

    @property
    def changed(self) -> bool:
        """If tag is different"""
        return self.tail != self.head
    
    @property
    def state(self) -> ImageEditorSceneTag:
        """Actual state"""
        if self.head == 0 and self.head == len(self.changes) - 1:
            return ImageEditorSceneTag.START
        elif self.head == 0:
            return ImageEditorSceneTag.FIRST
        elif self.head == len(self.changes) - 1:
            return ImageEditorSceneTag.LAST
        else:
            return ImageEditorSceneTag.MIDDLE
            
    @property
    def pixmap(self) -> QPixmap:
        return self.changes[self.head]
