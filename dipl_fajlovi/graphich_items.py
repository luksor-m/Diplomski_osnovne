import sys
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QPainter, QPen, QFont


class MapItemLocation(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, color):
        super().__init__(- radius,- radius, 2 * radius, 2 * radius)
        self.setPos(x, y)
        self.color = color
        self.update_color()

    def update_color(self):
        if self.color == "red":
            self.setPen(Qt.GlobalColor.red)
            self.setBrush(Qt.GlobalColor.red)
        elif self.color == "yellow":
            self.setPen(Qt.GlobalColor.yellow)
            self.setBrush(Qt.GlobalColor.yellow)

    def paint(self, painter, option, widget = None):
        view_scale = self.scene().views()[0].transform().m11()
        radius = self.rect().width() / 2 / view_scale
        rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawEllipse(rect)

class MapItemLink(QGraphicsLineItem):
    def __init__(self, x1, y1, x2,y2):
        super().__init__(x1, y1, x2, y2)
        self.start_pos = QPointF(x1, y1)
        self.end_pos = QPointF(x2, y2)
        self.update_position()

    def update_position(self):
        self.setLine(self.start_pos.x(), self.start_pos.y(), self.end_pos.x(), self.end_pos.y())

    def paint(self, painter, option, widget = None):
        view_scale = self.scene().views()[0].transform().m11()
        pen = QPen(Qt.GlobalColor.black, 2 / view_scale)
        painter.setPen(pen)
        painter.drawLine(self.line())


class MapItemText(QGraphicsTextItem):
    def __init__(self, x, y, text):
        super().__init__(text)
        self.setPos(x, y)

    def paint(self, painter, option, widget):
        view_scale = self.scene().views()[0].transform().m11()
        font = QFont()
        font.setPointSizeF(12 / view_scale)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), self.toPlainText())


class MapItemAntena(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, color):
        super().__init__(x1, y1, x2, y2)
        self.start_pos = QPointF(x1, y1)
        self.end_pos = QPointF(x2, y2)
        self.update_position()

        self.color = color

    def update_position(self):
        self.setLine(self.start_pos.x(), self.start_pos.y(), self.end_pos.x(), self.end_pos.y())

    def paint(self, painter, option, widget = None):
        view_scale = self.scene().views()[0].transform().m11()
        width_fac = 4
        if self.color == "yellow":
            pen = QPen(Qt.GlobalColor.yellow, width_fac / view_scale)
            painter.setPen(pen)
        else:
            pen = QPen(Qt.GlobalColor.blue, width_fac / view_scale)
            painter.setPen(pen)


        painter.drawLine(self.line())



