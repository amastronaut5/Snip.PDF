import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from capture.hotkey_manager import HotkeyWorker
from ui.main_window import MainWindow

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)

    # Initialize native worker
    worker = HotkeyWorker()
    worker.start()

    win = MainWindow(worker)
    win.show()

    exit_code = app.exec()

    worker.stop()
    sys.exit(exit_code)