from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication
from RinUI import RinUIWindow
from loguru import logger

from src.core import QML_PATH


class DebuggerCentral(QObject):
    def __init__(self, instance):
        super().__init__()
        self.instance = instance
        self.editor = None
        self.debugger_window = DebuggerWindow(self.instance, self)


    # @Slot()
    # def showEditor(self) -> None:
    #     logger.debug(f"Show Schedule Editor: {self.editor}")
    #     self.editor = ScheduleEditor(self.instance)
    #     self.editor.root_window.show()


class DebuggerWindow(RinUIWindow):
    def __init__(self, instance, parent=None):
        super().__init__()

        self.parent = parent
        self.engine.rootContext().setContextProperty("AppCentral", instance)
        self.engine.rootContext().setContextProperty("DebuggerCentral", self.parent)
        self.engine.addImportPath(QML_PATH)
        self.load(QML_PATH / "debugger" / "MainWindow.qml")


# class ScheduleEditor(RinUIWindow):
#     def __init__(self, instance, parent=None):
#         super().__init__()
#
#         self.parent = parent
#         self.engine.rootContext().setContextProperty("AppCentral", instance)
#         self.engine.addImportPath(QML_PATH)
#         self.load(QML_PATH / "debugger" / "EditSchedule.qml")


if __name__ == "__main__":
    app = QApplication()
    central = DebuggerCentral(None)
    # window = DebuggerWindow(None)
    # es_window = EditScheduleWindow(None)
    app.exec()
