from PySide6.QtWidgets import QApplication
from src.core import AppCentral
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)

    instance = AppCentral()
    instance.run()
    # debugger_central = DebuggerCentral(instance)
    # debugger = DebuggerWindow(instance)

    app.exec()
