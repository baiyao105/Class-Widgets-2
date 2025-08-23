from pathlib import Path
from PySide6.QtCore import QObject, Slot, Property, Signal, QRect, Qt
import RinUI
from PySide6.QtGui import QRegion
from loguru import logger

from src.core import QML_PATH


class WidgetsWindow(RinUI.RinUIWindow):
    def __init__(self, app_central):
        super().__init__()
        self.app_central = app_central
        self.display_mode_manager = WidgetDisplayModeManager()

        self._setup_qml_context()
        self.qml_main_path = Path(QML_PATH / "MainInterface.qml")

        self.engine.objectCreated.connect(self.on_qml_ready, type=Qt.ConnectionType.QueuedConnection)

    def _setup_qml_context(self):
        """设置QML上下文属性"""
        self.app_central.setup_qml_context(self)
        self.engine.rootContext().setContextProperty("DisplayModeManager", self.display_mode_manager)

    def run(self):
        """启动widgets窗口"""
        self.app_central.widgets_model.load_config()
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

    def on_qml_ready(self, obj, objUrl):
        if obj is None:
            logger.error("Main QML Load Failed")
            return

        widgets_loader = self.root_window.findChild(QObject, "widgetsLoader")
        if widgets_loader:
            widgets_loader.geometryChanged.connect(self.update_mask)
            return
        logger.error("'widgetsLoader' object has not found'")

    # 鼠标穿透
    def update_mask(self):
        mask = QRegion()
        widgets_loader = self.root_window.findChild(QObject, "widgetsLoader")
        if not widgets_loader:
            return

        menu_show = widgets_loader.property("menuVisible") or False
        edit_mode = widgets_loader.property("editMode") or False

        if menu_show or edit_mode:
            self.root_window.setMask(QRegion())
            return

        for w in widgets_loader.childItems():
            rect = QRect(
                int(w.x() + widgets_loader.x()),
                int(w.y() + widgets_loader.y()),
                int(w.width()),
                int(w.height())
            )
            mask = mask.united(QRegion(rect))

        self.root_window.setMask(mask)

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
