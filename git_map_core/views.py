from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt

class VistaMappa(QGraphicsView):
    """Vista interattiva con Zoom e Pan per la mappa."""
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def wheelEvent(self, event):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else (1.0 / 1.15)
        self.scale(zoom_factor, zoom_factor)

