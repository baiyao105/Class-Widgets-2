from pathlib import Path
from PySide6.QtCore import QObject, Slot, Property, Signal, QRect, Qt, QTimer
from PySide6.QtQml import QQmlComponent
import RinUI
from PySide6.QtGui import QRegion, QCursor
from PySide6.QtWidgets import QApplication
from loguru import logger

from src.core import QML_PATH


class WidgetsWindow(RinUI.RinUIWindow, QObject):
    themeReadyToReload = Signal()

    def __init__(self, app_central: QObject):
        super().__init__()
        self.app_central = app_central
        self.accepts_input = True
        self._theme_reloading = False

        self._setup_qml_context()
        self.qml_main_path = Path(QML_PATH / "MainInterface.qml")
        self.interactive_rect = QRegion()

        self.engine.objectCreated.connect(self.on_qml_ready, type=Qt.ConnectionType.QueuedConnection)

    def _setup_qml_context(self):
        """设置QML上下文属性"""
        self.app_central.setup_qml_context(self)

    def _start_listening(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_mouse_state)
        self.timer.start(33)  # 大约每秒30帧检测一次

    def run(self):
        """启动widgets窗口"""
        self.app_central.widgets_model.load_config()
        self._load_with_theme()
        self.app_central.theme_manager.themeChanged.connect(self.on_theme_changed)
        self.app_central.retranslate.connect(self.engine.retranslate)

    def _load_with_theme(self):
        """加载QML并应用主题"""
        current_theme_id = self.app_central.theme_manager.currentTheme
        if current_theme_id:
            current_theme_path = self.app_central.theme_manager.getThemePath(current_theme_id)
            if current_theme_path:
                self.engine.addImportPath(current_theme_path)
        self.load(self.qml_main_path)

        self._start_listening()

    def on_theme_changed(self):
        """主题变更时重新加载界面"""
        if self._theme_reloading:
            logger.info("Theme reload in progress, skipping")
            return
        
        self._theme_reloading = True
        logger.info("Theme changed, starting reload process")
        
        # 1. 获取当前主题路径
        current_theme_id = self.app_central.theme_manager.currentTheme
        if current_theme_id:
            current_theme_path = Path(self.app_central.theme_manager.getThemePath(current_theme_id))
            if current_theme_path:
                current_theme_path_str = str(current_theme_path).replace('\\', '/')  # 统一使用 / 分隔符
                paths = self.engine.importPathList()
                logger.info(f"Current import paths count: {len(paths)}")

                important_paths = []
                filtered_paths = []
                qml_path_str = str(QML_PATH).replace('\\', '/')  # 统一使用 / 分隔符
                logger.debug(f"QML_PATH string (normalized): {qml_path_str}")
                
                # 打印所有当前导入路径
                logger.debug("Current import paths:")
                for i, p in enumerate(paths):
                    normalized_p = p  # 统一使用 / 分隔符
                    logger.debug(f"  [{i}] {p}")
                    if qml_path_str in normalized_p:
                        important_paths.append(p)
                        logger.debug(f"  -> Keeping as important path")
                    # 移除其他主题路径（通过检查是否包含themes关键词）
                    elif "themes" in normalized_p.lower() and current_theme_path_str not in normalized_p:
                        logger.debug(f"  -> Removing old theme path")
                    else:
                        # 保留所有其他路径，包括插件路径
                        filtered_paths.append(p)
                        logger.debug(f"  -> Keeping as other path")
                
                # 构建最终路径列表：新主题路径 + 重要路径 + 其他路径
                final_paths = [current_theme_path_str] + important_paths + filtered_paths

                self.engine.setImportPathList(final_paths)
                logger.info(f"Set import path list, new path at index 0: {current_theme_path_str}")
                logger.info(f"Total paths: {len(final_paths)}")
                logger.info(f"Important paths kept: {len(important_paths)}")
                logger.info(f"Other paths kept: {len(filtered_paths)}")
        
        # 清除组件缓存
        self.engine.clearComponentCache()
        self.engine.collectGarbage()
        logger.info("Component cache cleared")
        
        # 触发 widget 重新加载
        self._trigger_widget_reload()
        self.engine.retranslate()
    
    def _trigger_widget_reload(self):
        """触发 widgets 重新加载"""
        logger.info("Triggering widget reload")
        self.app_central.theme_manager.themeReadyToReload.emit()

        self._theme_reloading = False
        logger.debug("Theme reloading flag reset to False")

    def on_qml_ready(self, obj, objUrl):
        if obj is None:
            logger.error("Main QML Load Failed")
            return

        widgets_loader = self.root_window.findChild(QObject, "widgetsLoader")
        if widgets_loader:
            widgets_loader.geometryChanged.connect(self.update_mask)
            return
        logger.error("'widgetsLoader' object has not found'")

    # 裁剪窗口
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
            if w.objectName() == "addWidgetsContainer":
                continue
            rect = QRect(
                int(w.x() + widgets_loader.x()),
                int(w.y() + widgets_loader.y()),
                int(w.width()),
                int(w.height())
            )
            mask = mask.united(QRegion(rect))

        self.interactive_rect = mask
        self.root_window.setMask(mask)

    def update_mouse_state(self):
        if not self.interactive_rect:
            return  # 没有 mask 就不处理
        if not self.app_central.configs.interactions.hover_fade:
            return  # 配置文件

        global_pos = QCursor.pos()
        # local_pos = self.widgets_loader.mapFromGlobal(global_pos)
        local_pos = global_pos

        in_mask = self.interactive_rect.contains(local_pos)

        if in_mask and not self.accepts_input:
            self.root_window.setProperty(
                "mouseHovered",
                True
            )
            self.root_window.show()
            self.accepts_input = True

            # 鼠标不在有效区域
        elif not in_mask and self.accepts_input:
            self.root_window.setProperty(
                "mouseHovered",
                False
            )
            self.root_window.show()
            self.accepts_input = False