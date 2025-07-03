from PySide6.QtGui import QGuiApplication
from src.core import AppCentral
import sys

from src.core.utils.debugger import DebuggerWindow

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    instance = AppCentral()
    instance.run()
    debugger = DebuggerWindow(instance)

    app.exec()
