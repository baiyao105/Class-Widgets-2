from pathlib import Path
from PySide6.QtCore import QObject, Slot, Property, Signal
from PySide6.QtQml import QQmlComponent, QQmlContext
import RinUI
from loguru import logger

from src.core import QML_PATH, PathManager
from src.core.plugin import PluginManager
from src.core.themes import ThemeManager
from .model import WidgetListModel


class WidgetsWindow(RinUI.RinUIWindow):
    def __init__(self, plugin_manager: PluginManager, theme_manager: ThemeManager, app_central, widget_model: WidgetListModel):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.theme_manager_ = theme_manager
        self.app_central = app_central
        self.display_mode_manager = WidgetDisplayModeManager()
        self.path_manager = PathManager()

        self.widget_model = widget_model
        self.engine.addImportPath(QML_PATH)
        self.engine.rootContext().setContextProperty("WidgetModel", self.widget_model)

        self.engine.rootContext().setContextProperty("ThemeManager", self.theme_manager_)
        self.engine.rootContext().setContextProperty("PluginManager", self.plugin_manager)
        self.engine.rootContext().setContextProperty("AppCentral", self.app_central)
        self.engine.rootContext().setContextProperty("DisplayModeManager", self.display_mode_manager)
        self.engine.rootContext().setContextProperty("PathManager", self.path_manager)

        self.qml_main_path = Path(QML_PATH / "MainInterface.qml")

    def run(self):
        self.widget_model.load_config()
        self.engine.addImportPath(str(self.theme_manager_.currentTheme))
        self.load(self.qml_main_path)
        self.theme_manager_.themeChanged.connect(self.on_theme_changed)

    def register_widget(self, widget_id: str, name: str, qml_path: str, backend_obj: QObject = None, icon: str = None):
        widget_data = {
            "id": widget_id,
            "name": name,
            "icon": icon or "",
            "qml_path": qml_path,
            "backend_obj": backend_obj,
        }

        self.widget_model.add_widget(widget_data)

    def on_theme_changed(self):
        self.engine.clearComponentCache()
        self.engine.addImportPath(str(self.theme_manager_.currentTheme))
        self.load(self.qml_main_path)


class WidgetDisplayModeManager(QObject):
    modeChanged = Signal()  # full -> mini 或 mini -> full

    def __init__(self):
        super().__init__()
        self._mode = "full"  # 默认完整模式

    @Property(str, notify=modeChanged)
    def mode(self):
        return self._mode

    @Slot(str)
    def setMode(self, new_mode):
        """设置模式（'full' 或 'mini'）"""
        if new_mode not in ("full", "mini"):
            return
        if self._mode != new_mode:
            self._mode = new_mode
            self.modeChanged.emit()

    @Slot()
    def toggleMode(self):
        """切换模式"""
        self.setMode("mini" if self._mode == "full" else "full")
