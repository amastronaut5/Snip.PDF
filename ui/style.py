class StyleSheet:
    DARK_THEME = """
    QMainWindow { background-color: #1E1E1E; }
    QWidget { color: #D4D4D4; font-family: 'Segoe UI'; font-size: 13px; }
    QListWidget { background-color: #252526; border: 1px solid #3C3C3C; border-radius: 4px; }
    QListWidget::item { background-color: #2D2D2D; margin-bottom: 4px; padding: 5px; border-radius: 4px; }
    QListWidget::item:selected { background-color: #37373D; border: 1px solid #007ACC; }
    QPushButton { background-color: #0E639C; color: #FFFFFF; border: none; padding: 6px 12px; border-radius: 4px; }
    QPushButton:hover { background-color: #1177BB; }
    QPushButton#secondaryButton { background-color: #3A3D3D; }
    QPushButton#dangerButton { background-color: #902626; }
    """