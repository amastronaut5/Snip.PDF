import logging
from PyQt6.QtCore import QThread, pyqtSignal
import ctypes
from ctypes import wintypes

logger = logging.getLogger(__name__)


class HotkeyWorker(QThread):
    """
    Registers a native Windows Global Hotkey.
    Gracefully handles locked hotkeys by trying fallback configurations automatically.
    """
    signal_trigger = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.user32 = ctypes.windll.user32
        self.HOTKEY_ID = 101  # Unique ID inside our application thread context
        self._running = True

        # Win32 Modifier Constants
        # MOD_CONTROL (0x0002), MOD_SHIFT (0x0004), MOD_ALT (0x0001)

        # Let's use Ctrl + Shift + F12 as primary (0x7B) because Windows Snipping Tool
        # heavily claims Ctrl+Shift+S on modern Windows 11/10 updates.
        self.primary_modifiers = 0x0002 | 0x0004  # Ctrl + Shift
        self.primary_key = 0x7B  # F12 Key

        # Alternate Option: Ctrl + Alt + S (0x53)
        self.fallback_modifiers = 0x0002 | 0x0001  # Ctrl + Alt
        self.fallback_key = 0x53  # 'S' Key

    def run(self):
        # Attempt Primary: Ctrl + Shift + F12
        success = self.user32.RegisterHotKey(None, self.HOTKEY_ID, self.primary_modifiers, self.primary_key)

        if success:
            logger.info("SUCCESS: Global hotkey [ Ctrl + Shift + F12 ] registered cleanly.")
        else:
            logger.warning("Ctrl+Shift+F12 was already occupied. Trying fallback option...")
            # Attempt Fallback: Ctrl + Alt + S
            success = self.user32.RegisterHotKey(None, self.HOTKEY_ID, self.fallback_modifiers, self.fallback_key)
            if success:
                logger.info("SUCCESS: Global hotkey [ Ctrl + Alt + S ] registered cleanly as fallback.")
            else:
                logger.error("CRITICAL: Both primary and fallback hotkeys are locked by other apps.")
                return

        msg = wintypes.MSG()
        while self._running:
            # Safe low-impact message polling loop
            if self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:  # WM_HOTKEY
                    if msg.wParam == self.HOTKEY_ID:
                        logger.info("Hotkey intercepted natively.")
                        self.signal_trigger.emit()
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))

    def stop(self):
        self._running = False
        self.user32.UnregisterHotKey(None, self.HOTKEY_ID)
        self.quit()
        self.wait()