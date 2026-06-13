import os

project_structure = {
    "requirements.txt": """PyQt6==6.7.0
Pillow==10.3.0
reportlab==4.2.0
keyboard==0.13.5""",

    "README.md": """# SnipPDF
Run an elevated command prompt and execute:
pip install -r requirements.txt
python main.py""",

    "capture/__init__.py": "",
    "ui/__init__.py": "",
    "pdf/__init__.py": "",

    "capture/hotkey_manager.py": """import logging
from PyQt6.QtCore import QObject, pyqtSignal
import keyboard

logger = logging.getLogger(__name__)

class GlobalHotkeyManager(QObject):
    hotkey_triggered = pyqtSignal()
    def __init__(self, hotkey_str: str = "ctrl+shift+s"):
        super().__init__()
        self.hotkey_str = hotkey_str
        self._is_registered = False
    def start(self):
        try:
            keyboard.add_hotkey(self.hotkey_str, self._on_hotkey_pressed)
            self._is_registered = True
            logger.info(f"Global hotkey '{self.hotkey_str}' registered.")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
    def stop(self):
        if self._is_registered:
            keyboard.remove_hotkey(self.hotkey_str)
            self._is_registered = False
    def _on_hotkey_pressed(self):
        self.hotkey_triggered.emit()""",

    "capture/capture_window.py": """import logging, io
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QPainter, QColor, QPen, QPixmap
from PyQt6.QtWidgets import QWidget
from PIL import Image

logger = logging.getLogger(__name__)

class CaptureScreenOverlay(QWidget):
    screenshot_captured = pyqtSignal(bytes)
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False
        self.full_screen_pixmap = QPixmap()
    def start_capture(self):
        screen = QGuiApplication.primaryScreen()
        if not screen: return
        geo = QGuiApplication.virtualGeometry()
        self.setGeometry(geo)
        self.full_screen_pixmap = screen.grabWindow(0, geo.x(), geo.y(), geo.width(), geo.height())
        self.showFullScreen()
        self.activateWindow()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.full_screen_pixmap)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        if self.is_selecting:
            rect = QRect(self.start_point, self.end_point).normalized()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)
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
        if event.key() == Qt.Key.Key_Escape: self.close()
    def _process_selection(self):
        rect = QRect(self.start_point, self.end_point).normalized()
        if rect.width() < 5 or rect.height() < 5: return
        qimage = self.full_screen_pixmap.copy(rect).toImage()
        buffer = io.BytesIO()
        ptr = qimage.bits()
        if ptr is not None:
            ptr.setsize(qimage.sizeInBytes())
            Image.frombuffer("RGBA", (qimage.width(), qimage.height()), ptr.asstring(), "raw", "RGBA", 0, 1).convert("RGB").save(buffer, format="PNG")
            self.screenshot_captured.emit(buffer.getvalue())""",

    "pdf/generator.py": """import logging, io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

logger = logging.getLogger(__name__)

class PDFGenerator:
    @staticmethod
    def generate(images_list: list[bytes], output_path: str) -> bool:
        if not images_list: return False
        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            pw, ph = letter
            for img_bytes in images_list:
                stream = io.BytesIO(img_bytes)
                iw, ih = Image.open(stream).size
                scale = min(pw / iw, ph / ih, 1.0)
                sw, sh = iw * scale, ih * scale
                c.drawImage(ImageReader(stream), (pw - sw)/2, (ph - sh)/2, width=sw, height=sh, mask='auto')
                c.showPage()
            c.save()
            return True
        except Exception as e:
            logger.error(f"PDF Error: {e}")
            return False""",

    "ui/style.py": """class StyleSheet:
    DARK_THEME = \"\"\"
    QMainWindow { background-color: #1E1E1E; }
    QWidget { color: #D4D4D4; font-family: 'Segoe UI'; font-size: 13px; }
    QListWidget { background-color: #252526; border: 1px solid #3C3C3C; border-radius: 4px; }
    QListWidget::item { background-color: #2D2D2D; margin-bottom: 4px; padding: 5px; border-radius: 4px; }
    QListWidget::item:selected { background-color: #37373D; border: 1px solid #007ACC; }
    QPushButton { background-color: #0E639C; color: #FFFFFF; border: none; padding: 6px 12px; border-radius: 4px; }
    QPushButton:hover { background-color: #1177BB; }
    QPushButton#secondaryButton { background-color: #3A3D3D; }
    QPushButton#dangerButton { background-color: #902626; }
    \"\"\"""",

    "ui/main_window.py": """import logging
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel, QFileDialog, QMessageBox
from capture.capture_window import CaptureScreenOverlay
from pdf.generator import PDFGenerator
from ui.style import StyleSheet

class MainWindow(QMainWindow):
    def __init__(self, hotkey_manager):
        super().__init__()
        self.setWindowTitle("SnipPDF Studio")
        self.setMinimumSize(700, 500)
        self.hotkey_manager = hotkey_manager
        self.captured_snippets = []
        self._init_ui()
        self.hotkey_manager.hotkey_triggered.connect(self.trigger_manual_snip)

    def _init_ui(self):
        self.setStyleSheet(StyleSheet.DARK_THEME)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        left = QVBoxLayout()
        left.addWidget(QLabel("SnipPDF Workspace (Ctrl+Shift+S)"))
        self.list_w = QListWidget()
        self.list_w.setIconSize(QSize(100, 75))
        left.addWidget(self.list_w)
        self.lbl_count = QLabel("Pages: 0 / 200")
        left.addWidget(self.lbl_count)
        layout.addLayout(left, 3)

        right = QVBoxLayout()
        self.btn_snip = QPushButton("Add Another Snip")
        self.btn_up = QPushButton("Move Up"); self.btn_up.setObjectName("secondaryButton")
        self.btn_down = QPushButton("Move Down"); self.btn_down.setObjectName("secondaryButton")
        self.btn_del = QPushButton("Delete Page"); self.btn_del.setObjectName("dangerButton")
        self.btn_pdf = QPushButton("Generate PDF")
        self.btn_new = QPushButton("New Session"); self.btn_new.setObjectName("secondaryButton")

        for b in [self.btn_snip, self.btn_up, self.btn_down, self.btn_del, self.btn_pdf, self.btn_new]:
            right.addWidget(b)
        right.addStretch()
        layout.addLayout(right, 1)

        self.btn_snip.clicked.connect(self.trigger_manual_snip)
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        self.btn_del.clicked.connect(self.delete_page)
        self.btn_pdf.clicked.connect(self.compile_pdf)
        self.btn_new.clicked.connect(self.clear_session)

    def trigger_manual_snip(self):
        if len(self.captured_snippets) >= 200: return
        self.overlay = CaptureScreenOverlay()
        self.overlay.screenshot_captured.connect(self.add_snip)
        self.overlay.start_capture()

    def add_snip(self, b):
        self.captured_snippets.append(b)
        px = QPixmap()
        px.loadFromData(b)
        item = QListWidgetItem(f"Page {self.list_w.count()+1}")
        item.setIcon(QIcon(px.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)))
        self.list_w.addItem(item)
        self.lbl_count.setText(f"Pages: {len(self.captured_snippets)} / 200")

    def delete_page(self):
        row = self.list_w.currentRow()
        if row >= 0:
            self.list_w.takeItem(row)
            self.captured_snippets.pop(row)
            self.lbl_count.setText(f"Pages: {len(self.captured_snippets)} / 200")

    def move_up(self):
        r = self.list_w.currentRow()
        if r > 0:
            self.captured_snippets[r], self.captured_snippets[r-1] = self.captured_snippets[r-1], self.captured_snippets[r]
            i = self.list_w.takeItem(r)
            self.list_w.insertItem(r-1, i)
            self.list_w.setCurrentRow(r-1)

    def move_down(self):
        r = self.list_w.currentRow()
        if 0 <= r < self.list_w.count() - 1:
            self.captured_snippets[r], self.captured_snippets[r+1] = self.captured_snippets[r+1], self.captured_snippets[r]
            i = self.list_w.takeItem(r)
            self.list_w.insertItem(r+1, i)
            self.list_w.setCurrentRow(r+1)

    def clear_session(self):
        self.captured_snippets.clear()
        self.list_w.clear()
        self.lbl_count.setText("Pages: 0 / 200")

    def compile_pdf(self):
        if not self.captured_snippets: return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if path:
            if PDFGenerator.generate(self.captured_snippets, path):
                QMessageBox.information(self, "Success", "PDF Generated!")""",

    "main.py": """import sys, os, logging
from PyQt6.QtWidgets import QApplication
from capture.hotkey_manager import GlobalHotkeyManager
from ui.main_window import MainWindow

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    app = QApplication(sys.argv)
    hk = GlobalHotkeyManager()
    hk.start()
    win = MainWindow(hk)
    win.show()
    sys.exit(app.exec())"""
}

# Generate directories and files
for path, content in project_structure.items():
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

print("Project Structure built successfully! Ready to run.")