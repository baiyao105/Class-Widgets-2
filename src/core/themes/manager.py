import json
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot, Property
from pathlib import Path

from loguru import logger

from src.core import SRC_PATH, QML_PATH
from src.core.directories import THEMES_PATH
from src.core.config import global_config

# @dataclass
# class ThemeMeta:
#     name: str
#     author: str
#     version: str


def verify(theme_ver):
    app_version = global_config.get("app").get("version")

    if theme_ver.strip() == "*":
        return True
    if theme_ver.startswith(">="):
        theme_ver = theme_ver[1:]
        return theme_ver >= app_version
    if theme_ver.startswith("<"):
        theme_ver = theme_ver[1:]
        return theme_ver >= app_version
    if theme_ver.startswith("="):
        theme_ver = theme_ver[1:]
        return theme_ver >= app_version
    return False


class ThemeManager(QObject):
    themeChanged = Signal()

    def __init__(self):
        super().__init__()
        # self._currentTheme = global_config.get("preferences").get("current_theme") or Path(QML_PATH / "widgets").as_uri()
        self._currentTheme = None
        # builtin 主题
        self._themes: dict = {}

    @Property(QObject, notify=themeChanged)
    def themes(self):
        return self._themes

    @Property(QObject, notify=themeChanged)
    def currentTheme(self):
        return self._currentTheme

    @Slot(str, result=bool)
    def themeChange(self, theme_path):
        for theme in self._themes:
            if theme == theme_path:
                self._currentTheme = theme
                self.themeChanged.emit()
                return True
        return False

    @Slot(str, result=dict)
    def load(self):
        # 读取主题
        self._themes = {
            Path(QML_PATH / "widgets"): {
                "name": "Default",
                "description": "Class Widgets Builtin Default Theme",
                "author": "RinLit",
                "version": "*",
            }
        }
        current_theme_exist = False

        if not THEMES_PATH.exists():
            THEMES_PATH.mkdir()
        for theme in THEMES_PATH.iterdir():
            if theme.is_dir():
                theme_meta = theme / "cwtheme.json"
                if theme_meta.exists():  # 读取
                    try:
                        with open(theme_meta, encoding="utf-8") as theme_json:
                            meta = json.load(theme_json)
                            if not verify(meta["theme"]):
                                logger.warning(f"Theme {theme.name} version is invalid (skipped)")
                                continue
                            self._themes[theme.as_uri()] = meta["theme"]

                            # 判断当前主题可用
                            if self._currentTheme == theme.as_uri():
                                current_theme_exist = True
                    except FileNotFoundError:
                        logger.warning(f"Theme '{theme.name}' cannot load. (FileNotFoundError)")
                    except PermissionError:
                        logger.warning(f"Theme '{theme.name}' cannot load. (PermissionError)")

        if not current_theme_exist:
            self._currentTheme = Path(QML_PATH / "builtin").as_uri()
            global_config["preferences"]["current_theme"] = self._currentTheme
            global_config.save_config()

        logger.info(f"Themes loaded: {len(self._themes)} themes")
        return self._themes
