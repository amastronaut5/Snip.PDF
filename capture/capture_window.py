import logging
import io
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QPainter, QColor, QPen, QPixmap
from PyQt6.QtWidgets import QWidget, QApplication
from PIL import Image

logger = logging.getLogger(__name__)


class CaptureScreenOverlay(QWidget):
    screenshot_captured = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        # Frameless tool window that stays completely on top
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False
        self.full_screen_pixmap = QPixmap()

    def start_capture(self):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            logger.error("Primary screen resolution lookup failed.")
            return

        # FIX: Query QApplication instead of QGuiApplication for virtual screen spaces
        geo = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geo)

        # Take an internal snapshot of the screen boundary before revealing overlay elements
        self.full_screen_pixmap = screen.grabWindow(0, geo.x(), geo.y(), geo.width(), geo.height())

        self.showFullScreen()
        self.activateWindow()
        logger.info("Snipping canvas overlay mapped and ready.")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.full_screen_pixmap)

        # Tint the screen with a 100-alpha dark mask overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if self.is_selecting:
            rect = QRect(self.start_point, self.end_point).normalized()
            # Punch a clear transparent hole right through the tint mask
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)

            # Draw a sleek VSCode blue boundary line around the clipping selection area
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(QPen(QColor(0, 122, 204), 2))
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.is_selecting = True

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.close()
            self._process_selection()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def _process_selection(self):
        rect = QRect(self.start_point, self.end_point).normalized()
        if rect.width() < 5 or rect.height() < 5:
            return

        qimage = self.full_screen_pixmap.copy(rect).toImage()
        buffer = io.BytesIO()
        ptr = qimage.bits()

        if ptr is not None:
            ptr.setsize(qimage.sizeInBytes())
            # Convert raw pixel buffers to PIL stream layout pipelines optimized for ReportLab inclusion
            Image.frombuffer(
                "RGBA", (qimage.width(), qimage.height()),
                ptr.asstring(), "raw", "RGBA", 0, 1
            ).convert("RGB").save(buffer, format="PNG")

            self.screenshot_captured.emit(buffer.getvalue())