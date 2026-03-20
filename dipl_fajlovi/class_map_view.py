from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsLineItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QWheelEvent, QMouseEvent


class map_view(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._pan = False
        self._pan_start_x = 0
        self._pan_start_y = 0
        self.__zoom_level = 1.0

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.1
        if event.angleDelta().y() > 0:
            factor = zoom_factor
            self.__zoom_level *= zoom_factor
        else:
            factor = 1 / zoom_factor
            self.__zoom_level /= zoom_factor

        # Center zoom on mouse position
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale(factor, factor)

        # Reset transformation if zoomed out too much
        if self.__zoom_level < 1.0:
            self.__zoom_level = 1.0
            self.resetTransform()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan = True
            self._pan_start_x = event.position().x()
            self._pan_start_y = event.position().y()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._pan:
            delta_x = event.position().x() - self._pan_start_x
            delta_y = event.position().y() - self._pan_start_y
            self._pan_start_x = event.position().x()
            self._pan_start_y = event.position().y()
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - delta_x))
            self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - delta_y))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

