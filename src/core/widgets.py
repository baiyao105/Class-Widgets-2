from pathlib import Path
from PySide6.QtCore import QObject, Slot, Property, Signal
from PySide6.QtQml import QQmlComponent, QQmlContext
from RinUI import RinUIWindow  # 假设你放在这里

from src.core import QML_PATH


class WidgetsWindow(RinUIWindow):
    def __init__(self, plugin_manager, theme_manager, app_central):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.theme_manager_ = theme_manager
        self.app_central = app_central
        self.display_mode_manager = WidgetDisplayModeManager()

        self.engine.addImportPath(str(self.theme_manager_.currentTheme))
        self.engine.rootContext().setContextProperty("ThemeManager", self.theme_manager)
        self.engine.rootContext().setContextProperty("PluginManager", self.plugin_manager)
        self.engine.rootContext().setContextProperty("AppCentral", self.app_central)
        self.engine.rootContext().setContextProperty("DisplayModeManager", self.display_mode_manager)

        self.qml_main_path = Path(QML_PATH / "WidgetsMain.qml")

        # 加载主界面
        self.load(self.qml_main_path)
        # self.load_widgets()

        # 监听主题切换信号
        self.theme_manager_.themeChanged.connect(self.on_theme_changed)

    def load_widgets(self):
        container = self.root_obj.findChild(QObject, "widgetContainer")
        if container is None:
            print("没有找到widgetContainer，检查 QML 结构是否正确！")
            return

        qml_paths = self.plugin_manager.get_all_qml_components()
        for qml_path in qml_paths:
            component = QQmlComponent(self.engine, str(qml_path))
            if component.status() == QQmlComponent.Ready:
                widget_obj = component.create()
                widget_obj.setParent(container)
                # 设置属性方便 QML 访问
                widget_obj.setProperty("themeManager", self.theme_manager_)
                widget_obj.setProperty("pluginManager", self.plugin_manager)
            else:
                print(f"组件加载失败: {qml_path}")

    def on_theme_changed(self):
        print("检测到主题变化，重新加载QML import路径和主界面")
        # 清除当前 importPath
        self.engine.clearComponentCache()

        self.engine.addImportPath(str(self.theme_manager_.currentTheme))

        # 重新加载主界面
        self.load(self.qml_main_path)

        # 重新加载插件
        self.load_widgets()


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
