# Built-in themes definition
from PySide6.QtCore import QCoreApplication

from src.core import ASSETS_PATH

BUILTIN_THEMES = [
    {
        "meta": {
            "id": "com.classwidgets.default",
            "name": "Default",
            "description": "Class Widgets Builtin Default Theme",
            "author": "Class Widgets Official",
            "version": "1.0.0",
            "api_version": "*",
            "preview": ASSETS_PATH / "images" / "themes" / "default.png",
        }
    }
]
