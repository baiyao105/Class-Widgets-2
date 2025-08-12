from pathlib import Path

from PySide6.QtCore import Slot
from loguru import logger

from src.core.plugin import CW2Plugin
from src.core.directories import QML_PATH

class Plugin(CW2Plugin):
    def on_load(self):
        self.api.register_widget(
            widget_id="hello_world",
            name="Hello World",
            qml_path=Path(QML_PATH/"widgets"/"test.qml").as_posix(),
            backend_obj=self,
        )

    @Slot()
    def sayHello(self):
        print("Hello World")

    def on_unload(self):
        print("[HelloWorld] Plugin unloaded!")
