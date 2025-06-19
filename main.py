import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QCursor

class MouseTracker(QWidget):
    EDGE_MARGIN = 8  # 边缘判定宽度
    def __init__(self):
        super().__init__()
        self.setWindowTitle('鼠标坐标与框选工具')
        self.setGeometry(100, 100, 800, 600)
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label = QLabel(self)
        self.label.move(10, 10)
        self.label.resize(300, 20)
        self.label.setStyleSheet('background:transparent;color:white;font-size:16px;')
        self.start_point = None
        self.end_point = None
        self.rect = None
        self.corners_label = QLabel(self)
        self.corners_label.move(10, 40)
        self.corners_label.resize(600, 60)
        self.corners_label.setStyleSheet('background:transparent;color:white;font-size:14px;')
        # 复制按钮
        self.copy_btn = QPushButton('复制坐标', self)
        self.copy_btn.move(10, 110)
        self.copy_btn.resize(100, 32)
        self.copy_btn.setStyleSheet('background:rgba(0,0,0,0.5);color:white;font-size:14px;border-radius:6px;')
        self.copy_btn.clicked.connect(self.copy_coords)
        # 右下角坐标label
        self.right_bottom_label = QLabel(self)
        self.right_bottom_label.resize(220, 24)
        self.right_bottom_label.setStyleSheet('background:transparent;color:yellow;font-size:14px;')
        self.update_right_bottom_label()
        # 缩放相关
        self.resizing = False
        self.resize_dir = None
        self.drag_pos = None

    def mouseMoveEvent(self, event):
        x, y = event.x(), event.y()
        self.label.setText(f'当前鼠标坐标: ({x}, {y})')
        self.update_right_bottom_label()
        if self.resizing:
            self.handle_resize(event.globalPos())
            return
        if self.start_point and not self.end_point:
            self.rect = QRect(self.start_point, event.pos())
            self.update()
        else:
            self.update_cursor(event.pos())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            dir = self.get_resize_dir(event.pos())
            if dir:
                self.resizing = True
                self.resize_dir = dir
                self.drag_pos = event.globalPos()
                self.old_geometry = self.geometry()
                return
            self.start_point = event.pos()
            self.end_point = None
            self.rect = None
            self.corners_label.clear()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.resizing:
                self.resizing = False
                self.resize_dir = None
                return
            if self.start_point:
                self.end_point = event.pos()
                self.rect = QRect(self.start_point, self.end_point)
                self.update()
                if self.rect:
                    x1, y1 = self.rect.topLeft().x(), self.rect.topLeft().y()
                    x2, y2 = self.rect.topRight().x(), self.rect.topRight().y()
                    x3, y3 = self.rect.bottomRight().x(), self.rect.bottomRight().y()
                    x4, y4 = self.rect.bottomLeft().x(), self.rect.bottomLeft().y()
                    self.corners_label.setText(
                        f'框选四角坐标:\n左上:({x1},{y1})  右上:({x2},{y2})  右下:({x3},{y3})  左下:({x4},{y4})'
                    )

    def resizeEvent(self, event):
        self.update_right_bottom_label()
        return super().resizeEvent(event)

    def update_right_bottom_label(self):
        w, h = self.width(), self.height()
        x, y = self.x(), self.y()
        rx, ry = w - 1, h - 1
        self.right_bottom_label.move(w - self.right_bottom_label.width() - 10, h - self.right_bottom_label.height() - 10)
        self.right_bottom_label.setText(f'窗口右下角: ({rx},{ry})')

    def copy_coords(self):
        clipboard = QApplication.clipboard()
        if self.rect:
            x1, y1 = self.rect.topLeft().x(), self.rect.topLeft().y()
            x2, y2 = self.rect.topRight().x(), self.rect.topRight().y()
            x3, y3 = self.rect.bottomRight().x(), self.rect.bottomRight().y()
            x4, y4 = self.rect.bottomLeft().x(), self.rect.bottomLeft().y()
            text = f'左上:({x1},{y1})  右上:({x2},{y2})  右下:({x3},{y3})  左下:({x4},{y4})'
        else:
            text = self.label.text()
        clipboard.setText(text)

    def update_cursor(self, pos):
        dir = self.get_resize_dir(pos)
        if dir == 'left' or dir == 'right':
            self.setCursor(Qt.SizeHorCursor)
        elif dir == 'top' or dir == 'bottom':
            self.setCursor(Qt.SizeVerCursor)
        elif dir == 'top_left' or dir == 'bottom_right':
            self.setCursor(Qt.SizeFDiagCursor)
        elif dir == 'top_right' or dir == 'bottom_left':
            self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def get_resize_dir(self, pos):
        x, y, w, h, m = pos.x(), pos.y(), self.width(), self.height(), self.EDGE_MARGIN
        left = x <= m
        right = x >= w - m
        top = y <= m
        bottom = y >= h - m
        if left and top:
            return 'top_left'
        if right and top:
            return 'top_right'
        if left and bottom:
            return 'bottom_left'
        if right and bottom:
            return 'bottom_right'
        if left:
            return 'left'
        if right:
            return 'right'
        if top:
            return 'top'
        if bottom:
            return 'bottom'
        return None

    def handle_resize(self, global_pos):
        dx = global_pos.x() - self.drag_pos.x()
        dy = global_pos.y() - self.drag_pos.y()
        g = self.old_geometry
        minw, minh = 200, 150
        x, y, w, h = g.x(), g.y(), g.width(), g.height()
        dir = self.resize_dir
        if 'left' in dir:
            new_x = min(x + dx, x + w - minw)
            new_w = max(w - dx, minw)
            self.setGeometry(new_x, y, new_w, h)
        if 'right' in dir:
            new_w = max(w + dx, minw)
            self.setGeometry(x, y, new_w, h)
        if 'top' in dir:
            new_y = min(y + dy, y + h - minh)
            new_h = max(h - dy, minh)
            self.setGeometry(x, new_y, w, new_h)
        if 'bottom' in dir:
            new_h = max(h + dy, minh)
            self.setGeometry(x, y, w, new_h)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

    def paintEvent(self, event):
        # 绘制窗口边框
        painter = QPainter(self)
        border_pen = QPen(Qt.blue)
        border_pen.setWidth(3)
        border_pen.setColor(Qt.blue)
        border_pen.setStyle(Qt.SolidLine)
        painter.setPen(border_pen)
        painter.setOpacity(0.5)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QWidget.rect(self).adjusted(1, 1, -2, -2))
        painter.setOpacity(1.0)
        # 绘制框选区域
        if self.rect:
            # 填充半透明白色
            painter.setBrush(Qt.white)
            painter.setOpacity(0.3)
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect)
            # 画红色虚线边框
            painter.setOpacity(1.0)
            pen = QPen(Qt.red, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MouseTracker()
    window.show()
    sys.exit(app.exec_()) 
