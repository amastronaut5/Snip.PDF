import logging
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel,
    QFileDialog, QMessageBox
)
from capture.capture_window import CaptureScreenOverlay
from pdf.generator import PDFGenerator
from ui.style import StyleSheet

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, hotkey_manager):
        super().__init__()
        self.setWindowTitle("SnipPDF Studio")
        self.setMinimumSize(700, 500)

        self.hotkey_manager = hotkey_manager
        self.captured_snippets = []
        self.overlays = []  # Explicitly preserve reference handles to block memory overrides

        self._init_ui()
        # Connect to the native Win32 wrapper signal safely
        self.hotkey_manager.signal_trigger.connect(self.trigger_manual_snip)

    def _init_ui(self):
        self.setStyleSheet(StyleSheet.DARK_THEME)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        left = QVBoxLayout()
        left.addWidget(QLabel("SnipPDF Workspace (Ctrl+Shift+S)"))
        self.list_w = QListWidget()
        self.list_w.setIconSize(QSize(100, 75))
        left.addWidget(QLabel("SnipPDF Workspace (Ctrl+Shift+F12 or Ctrl+Alt+S)"))
        self.lbl_count = QLabel("Pages: 0 / 200")
        left.addWidget(self.lbl_count)
        layout.addLayout(left, 3)

        right = QVBoxLayout()
        self.btn_snip = QPushButton("Add Another Snip")
        self.btn_up = QPushButton("Move Up");
        self.btn_up.setObjectName("secondaryButton")
        self.btn_down = QPushButton("Move Down");
        self.btn_down.setObjectName("secondaryButton")
        self.btn_del = QPushButton("Delete Page");
        self.btn_del.setObjectName("dangerButton")
        self.btn_pdf = QPushButton("Generate PDF")
        self.btn_new = QPushButton("New Session");
        self.btn_new.setObjectName("secondaryButton")

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

    @pyqtSlot()
    def trigger_manual_snip(self):
        if len(self.captured_snippets) >= 200:
            return

        try:
            overlay = CaptureScreenOverlay()
            overlay.screenshot_captured.connect(self.add_snip)
            # Store instance handle so Python 3.13 doesn't drop it mid-flight
            self.overlays.append(overlay)
            overlay.start_capture()
        except Exception as e:
            logger.error(f"Failed to initialize interface layer overlays: {e}")

    @pyqtSlot(bytes)
    def add_snip(self, b):
        self.captured_snippets.append(b)
        px = QPixmap()
        px.loadFromData(b)
        item = QListWidgetItem(f"Page {self.list_w.count() + 1}")
        item.setIcon(QIcon(px.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)))
        self.list_w.addItem(item)
        self.lbl_count.setText(f"Pages: {len(self.captured_snippets)} / 200")

        # Safe clean-up of finished overlays
        if self.overlays:
            self.overlays.pop(0)

    def delete_page(self):
        row = self.list_w.currentRow()
        if row >= 0:
            self.list_w.takeItem(row)
            self.captured_snippets.pop(row)
            self.lbl_count.setText(f"Pages: {len(self.captured_snippets)} / 200")

    def move_up(self):
        r = self.list_w.currentRow()
        if r > 0:
            self.captured_snippets[r], self.captured_snippets[r - 1] = self.captured_snippets[r - 1], \
            self.captured_snippets[r]
            i = self.list_w.takeItem(r)
            self.list_w.insertItem(r - 1, i)
            self.list_w.setCurrentRow(r - 1)

    def move_down(self):
        r = self.list_w.currentRow()
        if 0 <= r < self.list_w.count() - 1:
            self.captured_snippets[r], self.captured_snippets[r + 1] = self.captured_snippets[r + 1], \
            self.captured_snippets[r]
            i = self.list_w.takeItem(r)
            self.list_w.insertItem(r + 1, i)
            self.list_w.setCurrentRow(r + 1)

    def clear_session(self):
        self.captured_snippets.clear()
        self.list_w.clear()
        self.lbl_count.setText("Pages: 0 / 200")

    def compile_pdf(self):
        if not self.captured_snippets: return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if path:
            if PDFGenerator.generate(self.captured_snippets, path):
                QMessageBox.information(self, "Success", "PDF Generated successfully!")