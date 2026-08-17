import sys
import os

# Add the project root to Python path (parent directory of src)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, project_root)

from src.core import AppCentral
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    import qtlottie
    print(qtlottie.init_qml())  # 安装Lottie支持

    app = QApplication(sys.argv)
    instance = AppCentral()
    instance.run()
    app.exec()