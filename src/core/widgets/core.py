from pathlib import Path
from PySide6.QtCore import QObject, Slot, Property, Signal
import RinUI
from loguru import logger

from src.core import QML_PATH


class WidgetsWindow(RinUI.RinUIWindow):
    def __init__(self, app_central):
        super().__init__()
        self.app_central = app_central
        self.display_mode_manager = WidgetDisplayModeManager()
        
        self._setup_qml_context()
        self.qml_main_path = Path(QML_PATH / "MainInterface.qml")
    
    def _setup_qml_context(self):
        """设置QML上下文属性"""
        self.engine.addImportPath(QML_PATH)
        
        # 从AppCentral获取所有需要的组件
        context = self.engine.rootContext()
        context.setContextProperty("WidgetModel", self.app_central.widget_model)
        context.setContextProperty("ThemeManager", self.app_central.theme_manager)
        context.setContextProperty("PluginManager", self.app_central.plugin_manager)
        context.setContextProperty("AppCentral", self.app_central)
        context.setContextProperty("DisplayModeManager", self.display_mode_manager)
        context.setContextProperty("PathManager", self.app_central.path_manager)

    def run(self):
        """启动widgets窗口"""
        self.app_central.widget_model.load_config()
        self._load_with_theme()
        self.app_central.theme_manager.themeChanged.connect(self.on_theme_changed)
    
    def _load_with_theme(self):
        """加载QML并应用主题"""
        current_theme = self.app_central.theme_manager.currentTheme
        if current_theme:
            self.engine.addImportPath(str(current_theme))
        self.load(self.qml_main_path)

    def on_theme_changed(self):
        """主题变更时重新加载界面"""
        self.engine.clearComponentCache()
        self._load_with_theme()


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
