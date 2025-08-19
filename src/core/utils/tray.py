from pathlib import Path

from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon, QAction, QCursor
from PySide6.QtCore import QObject, Signal, Slot, QPoint
from loguru import logger

from src.core import ASSETS_PATH


class TrayIcon(QObject):
    togglePanel = Signal(QPoint)

    def __init__(self, parent=None):
        super().__init__()
        tray_icon_path = Path(ASSETS_PATH / "images" / "tray_icon.png").as_posix()
        self.tray = QSystemTrayIcon(QIcon(tray_icon_path))
        self.tray.setToolTip("Class Widgets 2")
        self.tray.activated.connect(self.on_click)
        self.tray.show()

    def on_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            pos = QCursor.pos()
            self.togglePanel.emit(pos)

    @Slot()
    def quitApp(self):
        import sys
        sys.exit(0)

    @Slot()
    def openSettings(self):
        print("打开设置面板！")
