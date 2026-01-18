from __future__ import annotations

from typing import List, Dict, Any, Optional

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from loguru import logger

from src.core.themes.loader import ThemeLoader, APP_API_VERSION
from src.core.directories import THEMES_PATH

DEFAULT_THEME_ID = "com.classwidgets.default"


class ThemeManager(QObject):
    themeChanged = Signal()
    themeListChanged = Signal()
    themeReadyToReload = Signal()

    def __init__(self, app_central, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._app_central = app_central
        self._themes: List[Dict[str, Any]] = []
        self._currentTheme: str = ""

        self._cooldown = QTimer(self)
        self._cooldown.setSingleShot(True)
        self._cooldown.setInterval(500)
        self._cooldown.timeout.connect(self._apply_pending)
        self._pending: Optional[str] = None

        self.loader = ThemeLoader()
        
        # 连接到 retranslate 信号
        app_central.retranslate.connect(self._on_retranslate)
        # self.scan()

    @Slot(result=list)
    def load(self):
        self.scan()
        return self._themes

    @Property('QVariant', notify=themeListChanged)
    def themes(self) -> List[Dict[str, Any]]:
        return list(self._themes)

    @Property(str, notify=themeChanged)
    def currentTheme(self) -> str:
        return self._currentTheme

    @Slot(result=str)
    def getAPIVersion(self) -> str:
        return str(APP_API_VERSION)

    @Slot(str, result=str)
    def getThemePath(self, theme_id: str) -> str:
        for theme in self._themes:
            if theme["id"] == theme_id:
                return theme.get("_path", "")
        return ""

    @Slot(str, result=dict)
    def getThemeById(self, theme_id: str):
        for theme in self._themes:
            if theme["id"] == theme_id:
                return theme
        return {}

    @Slot(str, result=bool)
    def themeChange(self, theme_id: str) -> bool:
        if theme_id == self._currentTheme:
            return True

        if not any(t["id"] == theme_id for t in self._themes):
            logger.warning(f"Unknown theme: {theme_id}")
            return False

        if self._cooldown.isActive():
            self._pending = theme_id
            return True

        self._apply(theme_id)
        self._cooldown.start()
        return True

    def scan(self) -> None:
        self._themes = self.loader.scan_themes(THEMES_PATH)
        self._currentTheme = self._app_central.configs.preferences.current_theme
        
        if not self._is_theme_valid(self._currentTheme):
            logger.warning(f"Current theme '{self._currentTheme}' is invalid, falling back to default theme")
            self._currentTheme = DEFAULT_THEME_ID
            self._app_central.configs.preferences.current_theme = DEFAULT_THEME_ID
        
        self.themeListChanged.emit()
        self.themeChanged.emit()

    def _apply_pending(self) -> None:
        if self._pending:
            self._apply(self._pending)
            self._pending = None

    def _is_theme_valid(self, theme_id: str) -> bool:
        return any(t["id"] == theme_id for t in self._themes)

    def _on_retranslate(self):
        """翻译变更时重新扫描主题以更新翻译"""
        logger.info("Retranslating themes...")
        self.scan()

    def _apply(self, theme_id: str) -> None:
        if not self._is_theme_valid(theme_id):
            logger.warning(f"Theme '{theme_id}' is invalid, falling back to default theme")
            theme_id = DEFAULT_THEME_ID
        
        self._currentTheme = theme_id
        self._app_central.configs.preferences.current_theme = theme_id
        logger.info(f"Theme switched to {theme_id}")
        self.themeChanged.emit()
